from flask import Blueprint, jsonify, request

from app.services.student_service import StudentService

api_bp = Blueprint("api", __name__)


def _json():
    return request.get_json(silent=True) or {}


@api_bp.route("/health", methods=["GET"])
def healthcheck():
    """Liveness / readiness endpoint for Docker and Kubernetes probes."""
    return jsonify({
        "status": "UP",
        "service": "Enterprise Student Record & Academic Management Platform",
        "version": "1.0.0",
    }), 200


@api_bp.route("/students", methods=["GET"])
def list_students():
    students = StudentService.list_students()
    return jsonify({"count": len(students), "students": students}), 200


@api_bp.route("/students", methods=["POST"])
def register_student():
    data = _json()
    try:
        student = StudentService.add_student(
            student_id=data.get("student_id"),
            name=data.get("name"),
            email=data.get("email"),
            program=data.get("program", "B.Tech CSE"),
            semester=data.get("semester", 1),
        )
        return jsonify({"message": "Student registered successfully",
                        "student": student}), 201
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400


@api_bp.route("/students/<student_id>", methods=["GET"])
def get_student(student_id):
    student = StudentService.get_student(student_id)
    if not student:
        return jsonify({"error": "Student not found"}), 404
    return jsonify(student), 200


@api_bp.route("/students/<student_id>/gpa", methods=["GET"])
def get_gpa(student_id):
    try:
        return jsonify(StudentService.calculate_gpa(student_id)), 200
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 404


@api_bp.route("/courses", methods=["GET"])
def list_courses():
    courses = StudentService.search_courses(request.args.get("q", ""))
    return jsonify({"count": len(courses), "courses": courses}), 200


@api_bp.route("/courses", methods=["POST"])
def add_course():
    data = _json()
    try:
        course = StudentService.add_course(
            course_id=data.get("course_id"),
            title=data.get("title"),
            credits=data.get("credits"),
            faculty_id=data.get("faculty_id"),
            slot=data.get("slot"),
            semester=data.get("semester", 3),
            capacity=data.get("capacity", 60),
        )
        return jsonify({"message": "Course added successfully", "course": course}), 201
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400


@api_bp.route("/enroll", methods=["POST"])
def enroll():
    data = _json()
    try:
        record = StudentService.enroll_student(data.get("student_id"), data.get("course_id"))
        return jsonify({"message": "Enrollment successful", "enrollment": record}), 200
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400


@api_bp.route("/drop", methods=["POST"])
def drop():
    data = _json()
    try:
        record = StudentService.drop_course(data.get("student_id"), data.get("course_id"))
        return jsonify({"message": "Course dropped successfully", "enrollment": record}), 200
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400


@api_bp.route("/marks", methods=["POST"])
def record_marks():
    data = _json()
    try:
        record = StudentService.record_marks(
            data.get("student_id"), data.get("course_id"), data.get("marks"))
        return jsonify({"message": "Marks recorded successfully", "result": record}), 200
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
