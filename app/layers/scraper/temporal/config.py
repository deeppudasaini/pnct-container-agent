from app.shared.config.settings.base import get_settings

settings = get_settings()

TEMPORAL_HOST = settings.TEMPORAL_HOST
TEMPORAL_PORT = settings.TEMPORAL_PORT
TEMPORAL_NAMESPACE = settings.TEMPORAL_NAMESPACE
TEMPORAL_TASK_QUEUE = settings.TEMPORAL_TASK_QUEUE
