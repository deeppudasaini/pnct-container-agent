from enum import Enum


class QueryIntent(str, Enum):
    GET_INFO = "get_info"
    CHECK_AVAILABILITY = "check_availability"
    GET_LOCATION = "get_location"
    CHECK_HOLDS = "check_holds"
    GET_LAST_FREE_DAY = "get_lfd"


class WorkflowStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"


class StepStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class ProcessingStep(str, Enum):
    VALIDATE_REQUEST = "validate_request"
    PARSE_QUERY = "parse_query"
    EXTRACT_ENTITIES = "extract_entities"
    CLASSIFY_INTENT = "classify_intent"
    SELECT_TOOL = "select_tool"
    TRIGGER_WORKFLOW = "trigger_workflow"
    INIT_BROWSER = "init_browser"
    SEARCH_CONTAINER = "search_container"
    EXTRACT_DATA = "extract_data"
    VALIDATE_DATA = "validate_data"
    STORE_DATA = "store_data"
    FORMAT_RESPONSE = "format_response"