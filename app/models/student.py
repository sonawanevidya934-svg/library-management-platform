class Student:
    """Student entity and schema validation."""

    @staticmethod
    def validate(data):
        if not isinstance(data, dict):
            return False, "Student data must be an object."
        for field in ("student_id", "name", "email"):
            value = data.get(field)
            if not isinstance(value, str) or not value.strip():
                return False, f"'{field}' is required."
        if "@" not in data["email"]:
            return False, "A valid email address is required."
        semester = data.get("semester", 1)
        if not isinstance(semester, int) or not 1 <= semester <= 8:
            return False, "Semester must be a number between 1 and 8."
        return True, None
