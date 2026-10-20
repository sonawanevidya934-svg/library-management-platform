import pytest

from app.services.student_service import StudentService


def test_enroll_student_success():
    record = StudentService.enroll_student("S101", "C301")
    assert record["status"] == "ACTIVE"
    assert record["enrollment_id"] == "E-0001"


def test_duplicate_enrollment_rejected():
    StudentService.enroll_student("S101", "C301")
    with pytest.raises(ValueError, match="already enrolled"):
        StudentService.enroll_student("S101", "C301")


def test_schedule_conflict_detected():
    # C301 and C303 are both on MON-09:00
    StudentService.enroll_student("S101", "C301")
    with pytest.raises(ValueError, match="Schedule conflict"):
        StudentService.enroll_student("S101", "C303")


def test_credit_limit_of_18_enforced():
    StudentService.add_course("X1", "Project I", 6, "F201", "SAT-09:00")
    StudentService.add_course("X2", "Project II", 6, "F201", "SAT-11:00")
    StudentService.add_course("X3", "Project III", 6, "F201", "SAT-14:00")
    StudentService.add_course("X4", "Seminar", 1, "F201", "SUN-09:00")
    StudentService.enroll_student("S101", "X1")
    StudentService.enroll_student("S101", "X2")
    StudentService.enroll_student("S101", "X3")  # exactly 18 credits
    with pytest.raises(ValueError, match="Credit limit exceeded"):
        StudentService.enroll_student("S101", "X4")


def test_course_capacity_enforced():
    StudentService.add_course("X9", "Tiny Class", 2, "F201", "SAT-09:00", capacity=1)
    StudentService.enroll_student("S101", "X9")
    with pytest.raises(ValueError, match="is full"):
        StudentService.enroll_student("S102", "X9")


def test_drop_course_frees_credits_and_slot():
    StudentService.enroll_student("S101", "C301")
    StudentService.drop_course("S101", "C301")
    # slot MON-09:00 is free again, so C303 can now be taken
    assert StudentService.enroll_student("S101", "C303")["status"] == "ACTIVE"
