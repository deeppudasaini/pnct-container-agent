
CONTAINER_ID_PATTERN = r"^[A-Z]{4}\d{7}$"

MAX_RETRIES = 3
RETRY_DELAY = 2
RETRY_BACKOFF = 2

PAGE_LOAD_TIMEOUT = 30000
ELEMENT_WAIT_TIMEOUT = 10000
NAVIGATION_TIMEOUT = 30000

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
]
