import structlog
import uvicorn

from ums.config import settings

logger = structlog.get_logger()


def main():
    uvicorn.run(
        "ums.gateway.app:create_app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
        log_level=settings.log_level.lower(),
        factory=True,
    )


if __name__ == "__main__":
    main()