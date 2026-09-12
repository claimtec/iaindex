"""
PDF report generation service with charts and recommendations
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path
import io
import logging
import base64

# PDF generation imports
try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.units import inch
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.colors import HexColor, Color
    from reportlab.lib import colors
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
        PageBreak, Image as RLImage
    )
    from reportlab.graphics.shapes import Drawing
    from reportlab.graphics.charts.barcharts import VerticalBarChart
    from reportlab.graphics.charts.piecharts import Pie
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

# Chart generation
try:
    import matplotlib
    matplotlib.use('Agg')  # Non-interactive backend
    import matplotlib.pyplot as plt
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

import boto3
from botocore.exceptions import ClientError

from ..config import settings

logger = logging.getLogger(__name__)


class PDFGenerator:
    """PDF report generator with charts and recommendations"""

    def __init__(self):
        self.s3_client = None
        self.bucket_name = settings.s3_bucket_snapshots
        self._setup_s3()

    def _setup_s3(self):
        """Set up S3 client for PDF storage"""
        try:
            self.s3_client = boto3.client('s3')
            logger.info("S3 client initialized for PDF storage")
        except Exception as e:
            logger.warning(f"S3 client not available: {e}")

    def generate_visibility_report(
        self,
        website_data: Dict[str, Any],
        visibility_data: Dict[str, Any],
        recommendations: List[Dict[str, Any]]
    ) -> io.BytesIO:
        """
        Generate comprehensive visibility report PDF

        Args:
            website_data: Website information
            visibility_data: Visibility scores and metrics
            recommendations: List of optimization recommendations

        Returns:
            PDF file as BytesIO buffer
        """
        if not REPORTLAB_AVAILABLE:
            logger.error("ReportLab not available. Cannot generate PDF.")
            raise RuntimeError("PDF generation library not installed")

        buffer = io.BytesIO()

        # Create PDF document
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )

        # Container for PDF elements
        story = []

        # Styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=HexColor('#2563eb'),
            spaceAfter=30
        )
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=HexColor('#1e40af'),
            spaceAfter=12
        )

        # Title
        title = Paragraph("AI Visibility Report", title_style)
        story.append(title)

        # Website info
        website_url = website_data.get('url', 'N/A')
        domain = website_data.get('domain', 'N/A')

        info_data = [
            ['Website:', website_url],
            ['Domain:', domain],
            ['Report Date:', datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')],
            ['Visibility Score:', f"{visibility_data.get('visibility_score', 0)}/100"]
        ]

        info_table = Table(info_data, colWidths=[2*inch, 4*inch])
        info_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.grey),
            ('TEXTCOLOR', (1, 0), (1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))

        story.append(info_table)
        story.append(Spacer(1, 20))

        # Visibility Score Section
        score_heading = Paragraph("Visibility Score Analysis", heading_style)
        story.append(score_heading)

        score = visibility_data.get('visibility_score', 0)
        score_text = self._get_score_interpretation(score)

        score_para = Paragraph(score_text, styles['Normal'])
        story.append(score_para)
        story.append(Spacer(1, 20))

        # Add chart if matplotlib is available
        if MATPLOTLIB_AVAILABLE:
            chart_buffer = self._generate_score_chart(visibility_data)
            if chart_buffer:
                img = RLImage(chart_buffer, width=5*inch, height=3*inch)
                story.append(img)
                story.append(Spacer(1, 20))

        # Recommendations Section
        rec_heading = Paragraph("Optimization Recommendations", heading_style)
        story.append(rec_heading)

        if recommendations:
            for i, rec in enumerate(recommendations[:10], 1):  # Top 10 recommendations
                priority = rec.get('priority', 'medium')
                title = rec.get('title', 'Recommendation')
                description = rec.get('description', '')

                # Priority badge
                priority_color = {
                    'critical': colors.red,
                    'high': colors.orange,
                    'medium': colors.blue,
                    'low': colors.green
                }.get(priority, colors.grey)

                rec_text = f"""
                <b><font color="{priority_color.hexval()}">[{priority.upper()}]</font> {i}. {title}</b><br/>
                {description}
                """

                rec_para = Paragraph(rec_text, styles['Normal'])
                story.append(rec_para)
                story.append(Spacer(1, 12))
        else:
            no_rec = Paragraph("No recommendations available at this time.", styles['Normal'])
            story.append(no_rec)

        story.append(Spacer(1, 20))

        # AI Mentions Section (if available)
        if visibility_data.get('ai_mentions'):
            mentions_heading = Paragraph("AI Search Engine Mentions", heading_style)
            story.append(mentions_heading)

            mentions = visibility_data['ai_mentions']
            for mention in mentions[:5]:  # Top 5
                query = mention.get('query', 'N/A')
                position = mention.get('position', 'N/A')
                engine = mention.get('engine', 'N/A')

                mention_text = f"<b>Query:</b> {query}<br/><b>Position:</b> {position}<br/><b>Engine:</b> {engine}"
                mention_para = Paragraph(mention_text, styles['Normal'])
                story.append(mention_para)
                story.append(Spacer(1, 10))

        # Footer
        story.append(PageBreak())
        footer = Paragraph(
            "Generated by <b>IAIndex</b> - AI Visibility Optimization Platform<br/>"
            "For more information, visit https://iaindex.org",
            styles['Normal']
        )
        story.append(footer)

        # Build PDF
        doc.build(story)

        buffer.seek(0)
        return buffer

    def _get_score_interpretation(self, score: int) -> str:
        """Get interpretation of visibility score"""
        if score >= 80:
            return f"<b>Excellent</b> (Score: {score}/100): Your website has strong AI visibility. " \
                   "Continue monitoring and maintain your optimization efforts."
        elif score >= 60:
            return f"<b>Good</b> (Score: {score}/100): Your website has decent AI visibility. " \
                   "Follow the recommendations below to improve further."
        elif score >= 40:
            return f"<b>Fair</b> (Score: {score}/100): Your website has moderate AI visibility. " \
                   "Significant improvements are possible with the recommended optimizations."
        elif score >= 20:
            return f"<b>Poor</b> (Score: {score}/100): Your website has low AI visibility. " \
                   "Immediate action is recommended to improve discoverability."
        else:
            return f"<b>Critical</b> (Score: {score}/100): Your website has very low AI visibility. " \
                   "Urgent optimization is needed to improve discoverability by AI systems."

    def _generate_score_chart(self, visibility_data: Dict[str, Any]) -> Optional[io.BytesIO]:
        """Generate visibility score chart"""
        if not MATPLOTLIB_AVAILABLE:
            return None

        try:
            fig, ax = plt.subplots(figsize=(8, 5))

            score = visibility_data.get('visibility_score', 0)

            # Create bar chart
            categories = ['Current\nScore', 'Industry\nAverage', 'Top\nPerformers']
            values = [score, 60, 90]  # Mock industry data
            colors_list = ['#2563eb', '#94a3b8', '#22c55e']

            bars = ax.bar(categories, values, color=colors_list)

            ax.set_ylim(0, 100)
            ax.set_ylabel('Visibility Score', fontsize=12)
            ax.set_title('AI Visibility Score Comparison', fontsize=14, fontweight='bold')

            # Add value labels on bars
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{int(height)}',
                       ha='center', va='bottom', fontsize=11, fontweight='bold')

            ax.grid(axis='y', alpha=0.3)

            # Save to buffer
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
            plt.close(fig)

            buffer.seek(0)
            return buffer

        except Exception as e:
            logger.error(f"Failed to generate chart: {e}")
            return None

    async def save_to_s3(self, pdf_buffer: io.BytesIO, file_path: str) -> Optional[str]:
        """
        Save PDF to S3 storage

        Args:
            pdf_buffer: PDF file buffer
            file_path: S3 object key

        Returns:
            Public URL of uploaded PDF or None if failed
        """
        if not self.s3_client:
            logger.warning("S3 client not available. Cannot save PDF.")
            return None

        try:
            pdf_buffer.seek(0)

            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=file_path,
                Body=pdf_buffer.read(),
                ContentType='application/pdf',
                ACL='public-read'
            )

            # Generate public URL
            url = f"https://{self.bucket_name}.s3.amazonaws.com/{file_path}"

            logger.info(f"PDF saved to S3: {file_path}")
            return url

        except ClientError as e:
            logger.error(f"Failed to save PDF to S3: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error saving PDF: {e}")
            return None

    async def generate_and_save(
        self,
        website_data: Dict[str, Any],
        visibility_data: Dict[str, Any],
        recommendations: List[Dict[str, Any]],
        user_id: str,
        website_id: str
    ) -> Optional[str]:
        """
        Generate PDF and save to S3

        Returns:
            Public URL of the PDF report
        """
        try:
            # Generate PDF
            pdf_buffer = self.generate_visibility_report(
                website_data=website_data,
                visibility_data=visibility_data,
                recommendations=recommendations
            )

            # Create S3 path
            timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
            file_path = f"reports/{user_id}/{website_id}/visibility_report_{timestamp}.pdf"

            # Save to S3
            url = await self.save_to_s3(pdf_buffer, file_path)

            return url

        except Exception as e:
            logger.error(f"Failed to generate and save PDF: {e}")
            return None


# Global PDF generator instance
pdf_generator = PDFGenerator()
