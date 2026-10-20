class Course:
    """Course entity and schema validation."""

    MAX_COURSE_CREDITS = 6

    @staticmethod
    def validate(data):
        if not isinstance(data, dict):
            return False, "Course data must be an object."
        for field in ("course_id", "title", "faculty_id", "slot"):
            value = data.get(field)
            if not isinstance(value, str) or not value.strip():
                return False, f"'{field}' is required."
        credits = data.get("credits")
        if (not isinstance(credits, int) or isinstance(credits, bool)
                or not 1 <= credits <= Course.MAX_COURSE_CREDITS):
            return False, "Credits must be a number between 1 and 6."
        capacity = data.get("capacity", 60)
        if not isinstance(capacity, int) or capacity < 1:
            return False, "Capacity must be at least 1."
        return True, None
