import pytest

from app.services.student_service import StudentService


def test_seeded_students_exist():
    assert len(StudentService.list_students()) == 2
    assert StudentService.get_student("S101")["name"] == "Aarav Sharma"


def test_add_student_success():
    student = StudentService.add_student("S200", "Grace Hopper", "grace@navy.mil", semester=5)
    assert student["student_id"] == "S200"
    assert student["semester"] == 5
    assert StudentService.get_student("S200") is not None


def test_add_duplicate_student_raises_error():
    with pytest.raises(ValueError, match="already exists"):
        StudentService.add_student("S101", "Duplicate Aarav", "dup@university.edu")


def test_add_student_rejects_invalid_email():
    with pytest.raises(ValueError, match="valid email"):
        StudentService.add_student("S300", "No Email", "not-an-email")


def test_delete_student_with_active_enrollment_fails():
    StudentService.enroll_student("S101", "C301")
    with pytest.raises(ValueError, match="active enrollments"):
        StudentService.delete_student("S101")
