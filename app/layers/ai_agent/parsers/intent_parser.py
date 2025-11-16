from app.shared.config.constants.app_constants import QueryIntent


class IntentParser:
    def classify_intent(self, parsed_query: dict) -> str:
        intent = parsed_query.get("intent", "").lower()

        if intent in ["get_info", "info", "information", "details"]:
            return QueryIntent.GET_INFO
        elif intent in ["check_availability", "available", "pickup"]:
            return QueryIntent.CHECK_AVAILABILITY
        elif intent in ["get_location", "location", "where"]:
            return QueryIntent.GET_LOCATION
        elif intent in ["check_holds", "holds", "restrictions"]:
            return QueryIntent.CHECK_HOLDS
        elif intent in ["get_lfd", "last_free_day", "lfd"]:
            return QueryIntent.GET_LAST_FREE_DAY

        return QueryIntent.GET_INFO
