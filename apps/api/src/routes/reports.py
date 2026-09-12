"""
Report generation and delivery routes
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request, BackgroundTasks
from pydantic import BaseModel, HttpUrl
from typing import Dict, Any, Optional, List
from datetime import datetime
import logging

from supabase import create_client, Client

from ..config import settings
from ..middleware.auth import get_current_user
from ..services.pdf_generator import pdf_generator
from ..services.email_service import email_service
from ..utils.exceptions import ResourceNotFoundError, DatabaseError, ServiceUnavailableError

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/v1/reports", tags=["reports"])


async def get_supabase_client() -> Client:
    """Get Supabase client"""
    return create_client(settings.supabase_url, settings.supabase_key)


class GenerateReportRequest(BaseModel):
    """Request model for report generation"""
    website_id: str
    include_charts: bool = True
    send_email: bool = False


class ReportResponse(BaseModel):
    """Response model for report"""
    report_id: str
    website_id: str
    report_url: str
    created_at: datetime
    visibility_score: int


class EmailReportRequest(BaseModel):
    """Request model for email delivery"""
    report_id: str
    recipient_email: Optional[str] = None


@router.post("/generate", response_model=ReportResponse)
async def generate_report(
    request_data: GenerateReportRequest,
    background_tasks: BackgroundTasks,
    current_user: Dict[str, Any] = Depends(get_current_user),
    supabase: Client = Depends(get_supabase_client)
):
    """
    Generate PDF visibility report for a website

    - **website_id**: ID of the website to generate report for
    - **include_charts**: Include visualization charts (default: true)
    - **send_email**: Send report via email after generation (default: false)

    Returns report URL for download.
    """
    try:
        user_id = current_user.get("sub")
        website_id = request_data.website_id

        # Get website data
        website_result = supabase.table("websites").select("*").eq(
            "id", website_id
        ).eq("user_id", user_id).execute()

        if not website_result.data:
            raise ResourceNotFoundError(resource="Website")

        website = website_result.data[0]

        # Get latest visibility data
        visibility_result = supabase.table("ai_mentions").select("*").eq(
            "website_id", website_id
        ).order("created_at", desc=True).limit(1).execute()

        visibility_data = {
            "visibility_score": website.get("visibility_score", 0),
            "ai_mentions": visibility_result.data if visibility_result.data else []
        }

        # Get recommendations
        recommendations_result = supabase.table("recommendations").select("*").eq(
            "website_id", website_id
        ).order("priority", desc=True).execute()

        recommendations = recommendations_result.data if recommendations_result.data else []

        # Generate PDF
        logger.info(f"Generating PDF report for website {website_id}")

        report_url = await pdf_generator.generate_and_save(
            website_data=website,
            visibility_data=visibility_data,
            recommendations=recommendations,
            user_id=user_id,
            website_id=website_id
        )

        if not report_url:
            raise ServiceUnavailableError(detail="Failed to generate PDF report")

        # Save report record
        report_data = {
            "user_id": user_id,
            "website_id": website_id,
            "report_url": report_url,
            "visibility_score": visibility_data["visibility_score"],
            "created_at": datetime.utcnow().isoformat()
        }

        report_result = supabase.table("reports").insert(report_data).execute()

        if not report_result.data:
            raise DatabaseError(detail="Failed to save report")

        report = report_result.data[0]

        # Send email in background if requested
        if request_data.send_email:
            user_email = current_user.get("email")
            if user_email:
                background_tasks.add_task(
                    email_service.send_pdf_report_email,
                    user_email=user_email,
                    website_url=website.get("url"),
                    report_url=report_url,
                    visibility_score=visibility_data["visibility_score"]
                )

        logger.info(f"Report generated successfully: {report['id']}")

        return ReportResponse(
            report_id=report["id"],
            website_id=website_id,
            report_url=report_url,
            created_at=datetime.fromisoformat(report["created_at"]),
            visibility_score=visibility_data["visibility_score"]
        )

    except (ResourceNotFoundError, ServiceUnavailableError, DatabaseError):
        raise
    except Exception as e:
        logger.error(f"Failed to generate report: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate report"
        )


@router.post("/email")
async def email_report(
    request_data: EmailReportRequest,
    background_tasks: BackgroundTasks,
    current_user: Dict[str, Any] = Depends(get_current_user),
    supabase: Client = Depends(get_supabase_client)
):
    """
    Send existing report via email

    - **report_id**: ID of the report to send
    - **recipient_email**: Optional recipient email (defaults to user's email)
    """
    try:
        user_id = current_user.get("sub")
        user_email = current_user.get("email")

        # Get report
        report_result = supabase.table("reports").select("*").eq(
            "id", request_data.report_id
        ).eq("user_id", user_id).execute()

        if not report_result.data:
            raise ResourceNotFoundError(resource="Report")

        report = report_result.data[0]

        # Get website data
        website_result = supabase.table("websites").select("*").eq(
            "id", report["website_id"]
        ).execute()

        if not website_result.data:
            raise ResourceNotFoundError(resource="Website")

        website = website_result.data[0]

        # Determine recipient
        recipient = request_data.recipient_email or user_email

        # Send email in background
        background_tasks.add_task(
            email_service.send_pdf_report_email,
            user_email=recipient,
            website_url=website.get("url"),
            report_url=report["report_url"],
            visibility_score=report.get("visibility_score", 0)
        )

        logger.info(f"Report email queued for {recipient}")

        return {
            "message": "Report email queued for delivery",
            "recipient": recipient,
            "report_id": request_data.report_id
        }

    except (ResourceNotFoundError,):
        raise
    except Exception as e:
        logger.error(f"Failed to email report: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send report email"
        )


@router.get("/{report_id}", response_model=ReportResponse)
async def get_report(
    report_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
    supabase: Client = Depends(get_supabase_client)
):
    """
    Get report details by ID

    Returns report information including download URL.
    """
    try:
        user_id = current_user.get("sub")

        # Get report
        result = supabase.table("reports").select("*").eq(
            "id", report_id
        ).eq("user_id", user_id).execute()

        if not result.data:
            raise ResourceNotFoundError(resource="Report")

        report = result.data[0]

        return ReportResponse(
            report_id=report["id"],
            website_id=report["website_id"],
            report_url=report["report_url"],
            created_at=datetime.fromisoformat(report["created_at"]),
            visibility_score=report.get("visibility_score", 0)
        )

    except ResourceNotFoundError:
        raise
    except Exception as e:
        logger.error(f"Failed to get report: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve report"
        )


@router.get("/website/{website_id}", response_model=List[ReportResponse])
async def list_reports_for_website(
    website_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
    supabase: Client = Depends(get_supabase_client)
):
    """
    List all reports for a specific website

    Returns list of reports ordered by creation date (newest first).
    """
    try:
        user_id = current_user.get("sub")

        # Verify website ownership
        website_result = supabase.table("websites").select("id").eq(
            "id", website_id
        ).eq("user_id", user_id).execute()

        if not website_result.data:
            raise ResourceNotFoundError(resource="Website")

        # Get reports
        result = supabase.table("reports").select("*").eq(
            "website_id", website_id
        ).order("created_at", desc=True).execute()

        reports = result.data or []

        return [
            ReportResponse(
                report_id=report["id"],
                website_id=report["website_id"],
                report_url=report["report_url"],
                created_at=datetime.fromisoformat(report["created_at"]),
                visibility_score=report.get("visibility_score", 0)
            )
            for report in reports
        ]

    except ResourceNotFoundError:
        raise
    except Exception as e:
        logger.error(f"Failed to list reports: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve reports"
        )
