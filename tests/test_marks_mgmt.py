import pytest

from app.services.student_service import StudentService


def test_grade_point_scale():
    assert StudentService.grade_point(95) == (10, "O")
    assert StudentService.grade_point(85) == (9, "A+")
    assert StudentService.grade_point(72) == (8, "A")
    assert StudentService.grade_point(41) == (4, "P")
    assert StudentService.grade_point(30) == (0, "F")


def test_record_marks_requires_enrollment():
    with pytest.raises(ValueError, match="not enrolled"):
        StudentService.record_marks("S101", "C301", 80)


def test_record_marks_rejects_out_of_range():
    StudentService.enroll_student("S101", "C301")
    with pytest.raises(ValueError, match="between 0 and 100"):
        StudentService.record_marks("S101", "C301", 120)


def test_gpa_calculation_is_credit_weighted():
    for course in ("C301", "C302", "C304"):
        StudentService.enroll_student("S101", course)
    StudentService.record_marks("S101", "C301", 85)  # 9 points x 4 credits
    StudentService.record_marks("S101", "C302", 72)  # 8 points x 4 credits
    StudentService.record_marks("S101", "C304", 95)  # 10 points x 3 credits
    result = StudentService.calculate_gpa("S101")
    assert result["total_credits"] == 11
    assert result["gpa"] == 8.91  # (36 + 32 + 30) / 11


def test_gpa_is_zero_without_marks():
    assert StudentService.calculate_gpa("S102")["gpa"] == 0.0
