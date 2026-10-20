from datetime import datetime, timezone

from app.models.course import Course
from app.models.student import Student
from database.db import db

MAX_CREDITS_PER_SEMESTER = 18

# (minimum marks, grade points, letter grade) - 10 point scale
GRADE_SCALE = [
    (90, 10, "O"), (80, 9, "A+"), (70, 8, "A"), (60, 7, "B+"),
    (50, 6, "B"), (45, 5, "C"), (40, 4, "P"), (0, 0, "F"),
]


def _now():
    return datetime.now(timezone.utc).isoformat()


def _active_enrollment(student_id, course_id):
    for enrol in db.enrollments:
        if (enrol["student_id"] == student_id and enrol["course_id"] == course_id
                and enrol["status"] == "ACTIVE"):
            return enrol
    return None


class StudentService:
    """Business rules for the student record and academic platform."""

    # ---------------- students ----------------
    @staticmethod
    def add_student(student_id, name, email, program="B.Tech CSE", semester=1):
        payload = {"student_id": student_id, "name": name,
                   "email": email, "semester": semester}
        valid, error = Student.validate(payload)
        if not valid:
            raise ValueError(error)
        with db.lock:
            if student_id in db.students:
                raise ValueError(f"Student with ID '{student_id}' already exists.")
            record = {"student_id": student_id, "name": name.strip(), "email": email,
                      "program": program, "semester": semester}
            db.students[student_id] = record
            return record

    @staticmethod
    def get_student(student_id):
        return db.students.get(student_id)

    @staticmethod
    def list_students():
        return list(db.students.values())

    @staticmethod
    def delete_student(student_id):
        with db.lock:
            if student_id not in db.students:
                raise ValueError(f"Student '{student_id}' not found.")
            for enrol in db.enrollments:
                if enrol["student_id"] == student_id and enrol["status"] == "ACTIVE":
                    raise ValueError(
                        f"Cannot delete student '{student_id}' with active enrollments.")
            del db.students[student_id]
            return True

    # ---------------- courses ----------------
    @staticmethod
    def add_course(course_id, title, credits, faculty_id, slot, semester=3, capacity=60):
        payload = {"course_id": course_id, "title": title, "credits": credits,
                   "faculty_id": faculty_id, "slot": slot, "capacity": capacity}
        valid, error = Course.validate(payload)
        if not valid:
            raise ValueError(error)
        with db.lock:
            if course_id in db.courses:
                raise ValueError(f"Course with ID '{course_id}' already exists.")
            if faculty_id not in db.faculty:
                raise ValueError(f"Faculty '{faculty_id}' not found.")
            record = {"course_id": course_id, "title": title.strip(), "credits": credits,
                      "faculty_id": faculty_id, "slot": slot, "semester": semester,
                      "capacity": capacity}
            db.courses[course_id] = record
            return record

    @staticmethod
    def get_course(course_id):
        return db.courses.get(course_id)

    @staticmethod
    def search_courses(query=""):
        q = query.lower().strip()
        if not q:
            return list(db.courses.values())
        return [c for c in db.courses.values()
                if q in c["title"].lower() or q in c["course_id"].lower()]

    # ---------------- enrollment ----------------
    @staticmethod
    def enroll_student(student_id, course_id):
        with db.lock:
            if student_id not in db.students:
                raise ValueError(f"Student '{student_id}' not registered.")
            course = db.courses.get(course_id)
            if not course:
                raise ValueError(f"Course '{course_id}' not found in catalog.")

            active = [e for e in db.enrollments if e["status"] == "ACTIVE"]
            mine = [e for e in active if e["student_id"] == student_id]

            if any(e["course_id"] == course_id for e in mine):
                raise ValueError(f"Student '{student_id}' is already enrolled in '{course_id}'.")

            seats_taken = sum(1 for e in active if e["course_id"] == course_id)
            if seats_taken >= course["capacity"]:
                raise ValueError(f"Course '{course['title']}' is full.")

            for enrol in mine:
                other = db.courses[enrol["course_id"]]
                if other["slot"] == course["slot"]:
                    raise ValueError(
                        f"Schedule conflict with '{other['title']}' at {course['slot']}.")

            used = sum(db.courses[e["course_id"]]["credits"] for e in mine
                       if db.courses[e["course_id"]]["semester"] == course["semester"])
            if used + course["credits"] > MAX_CREDITS_PER_SEMESTER:
                raise ValueError(
                    f"Credit limit exceeded (Max: {MAX_CREDITS_PER_SEMESTER} "
                    f"credits per semester).")

            record = {
                "enrollment_id": f"E-{len(db.enrollments) + 1:04d}",
                "student_id": student_id, "course_id": course_id,
                "enrolled_at": _now(), "status": "ACTIVE",
            }
            db.enrollments.append(record)
            return record

    @staticmethod
    def drop_course(student_id, course_id):
        with db.lock:
            if student_id not in db.students or course_id not in db.courses:
                raise ValueError("Invalid student or course ID.")
            enrol = _active_enrollment(student_id, course_id)
            if not enrol:
                raise ValueError(
                    f"No active enrollment for student '{student_id}' in '{course_id}'.")
            enrol["status"] = "DROPPED"
            enrol["dropped_at"] = _now()
            db.marks.pop(f"{student_id}:{course_id}", None)
            return enrol

    # ---------------- marks & GPA ----------------
    @staticmethod
    def grade_point(marks):
        for minimum, points, letter in GRADE_SCALE:
            if marks >= minimum:
                return points, letter
        return 0, "F"

    @staticmethod
    def record_marks(student_id, course_id, marks):
        if (not isinstance(marks, (int, float)) or isinstance(marks, bool)
                or not 0 <= marks <= 100):
            raise ValueError("Marks must be a number between 0 and 100.")
        with db.lock:
            if student_id not in db.students or course_id not in db.courses:
                raise ValueError("Invalid student or course ID.")
            if not _active_enrollment(student_id, course_id):
                raise ValueError(
                    f"Student '{student_id}' is not enrolled in '{course_id}'.")
            points, letter = StudentService.grade_point(marks)
            record = {"student_id": student_id, "course_id": course_id,
                      "marks": marks, "grade_points": points, "grade": letter}
            db.marks[f"{student_id}:{course_id}"] = record
            return record

    @staticmethod
    def calculate_gpa(student_id):
        with db.lock:
            if student_id not in db.students:
                raise ValueError(f"Student '{student_id}' not found.")
            total_points = 0
            total_credits = 0
            graded = 0
            for key, rec in db.marks.items():
                if rec["student_id"] != student_id:
                    continue
                credits = db.courses[rec["course_id"]]["credits"]
                total_points += rec["grade_points"] * credits
                total_credits += credits
                graded += 1
            gpa = round(total_points / total_credits, 2) if total_credits else 0.0
            return {"student_id": student_id, "gpa": gpa,
                    "total_credits": total_credits, "courses_graded": graded}
