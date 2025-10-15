"""
Main FastAPI application for IA Index Verification API
"""
from fastapi import FastAPI, Request, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import logging
from datetime import datetime
from contextlib import asynccontextmanager

from .config import settings
from .routes import receipts, analytics, publishers, attestations

# Configure logging
logging.basicConfig(
    level=logging.INFO if not settings.debug else logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)


# Lifespan context manager for startup/shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager"""
    logger.info("Starting IA Index Verification API")
    logger.info(f"Environment: {'Development' if settings.debug else 'Production'}")
    yield
    logger.info("Shutting down IA Index Verification API")


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="""
    IA Index Verification API provides endpoints for receipt verification,
    publisher domain verification, and cryptographic attestations.

    ## Features

    * **Receipt Management**: Ingest and verify publisher receipts
    * **Domain Verification**: Verify publisher domains via DNS, HTML, or file upload
    * **Analytics**: Track receipt statistics and publisher analytics
    * **Attestations**: Daily Merkle tree attestations for cryptographic proof
    * **Authentication**: JWT and API key-based authentication
    * **Rate Limiting**: Protection against abuse

    ## Authentication

    Most endpoints require authentication via:
    - Bearer token (JWT): `Authorization: Bearer <token>`
    - API key: `X-API-Key: <api-key>`

    Use `/v1/auth/login` to obtain a JWT token.
    """,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

# Add rate limiter to app state
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-RateLimit-Limit", "X-RateLimit-Remaining", "X-RateLimit-Reset"]
)


# Exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "timestamp": datetime.utcnow().isoformat()
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal server error",
            "status_code": 500,
            "timestamp": datetime.utcnow().isoformat()
        }
    )


# Middleware for logging requests
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all requests"""
    start_time = datetime.utcnow()

    # Log request
    logger.info(f"{request.method} {request.url.path} - Start")

    # Process request
    response = await call_next(request)

    # Log response
    duration = (datetime.utcnow() - start_time).total_seconds()
    logger.info(
        f"{request.method} {request.url.path} - "
        f"Status: {response.status_code} - "
        f"Duration: {duration:.3f}s"
    )

    return response


# Health check endpoint
@app.get("/health", tags=["system"])
@limiter.limit("100/minute")
async def health_check(request: Request):
    """
    Health check endpoint

    Returns the API status and version information.
    """
    return {
        "status": "healthy",
        "version": settings.app_version,
        "timestamp": datetime.utcnow().isoformat(),
        "service": "iaindex-verification-api"
    }


# Root endpoint
@app.get("/", tags=["system"])
async def root():
    """
    Root endpoint

    Returns basic API information and links to documentation.
    """
    return {
        "message": "IA Index Verification API",
        "version": settings.app_version,
        "docs": "/docs",
        "redoc": "/redoc",
        "health": "/health"
    }


# Authentication endpoint
@app.post("/v1/auth/login", tags=["authentication"])
@limiter.limit(settings.rate_limit_per_minute)
async def login(request: Request, username: str, password: str):
    """
    Login endpoint for API key authentication

    Returns a JWT token for authenticated access to protected endpoints.

    Note: This is a placeholder implementation. In production, implement
    proper user authentication with password hashing and database lookup.
    """
    from .middleware.auth import AuthService

    # TODO: Implement proper authentication
    # This is a placeholder - implement database lookup and password verification
    if username == "admin" and password == "changeme":
        token = AuthService.create_access_token(
            data={"sub": username, "type": "user"}
        )
        return {
            "access_token": token,
            "token_type": "bearer",
            "expires_in": settings.access_token_expire_minutes * 60
        }

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid credentials"
    )


# Public endpoint for verified domains (alias for convenience)
@app.get("/v1/verified-domains", tags=["publishers"])
@limiter.limit(settings.rate_limit_per_hour)
async def get_verified_domains_alias(request: Request):
    """
    Get list of verified publisher domains (public endpoint)

    Alias for /v1/publishers/verified-domains
    """
    from .routes.publishers import get_verified_domains, get_supabase_client

    supabase = await get_supabase_client()
    return await get_verified_domains(request, None, supabase)


# Include routers
app.include_router(receipts.router)
app.include_router(analytics.router)
app.include_router(publishers.router)
app.include_router(attestations.router)


# Run with: uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level="info"
    )
