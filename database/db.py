import threading


class Database:
    """Thread-safe, in-memory data store (singleton) with seed data."""

    _instance = None
    _singleton_lock = threading.Lock()

    def __new__(cls):
        with cls._singleton_lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._init_db()
            return cls._instance

    def _init_db(self):
        self.lock = threading.RLock()
        self.students = {}
        self.faculty = {}
        self.courses = {}
        self.enrollments = []
        self.marks = {}
        self._seed_initial_data()

    def _seed_initial_data(self):
        self.students["S101"] = {
            "student_id": "S101", "name": "Aarav Sharma",
            "email": "aarav.sharma@university.edu",
            "program": "B.Tech CSE", "semester": 3,
        }
        self.students["S102"] = {
            "student_id": "S102", "name": "Priya Patil",
            "email": "priya.patil@university.edu",
            "program": "B.Tech CSE", "semester": 3,
        }
        self.faculty["F201"] = {
            "faculty_id": "F201", "name": "Dr. Meera Kulkarni",
            "department": "Computer Science",
        }
        self.faculty["F202"] = {
            "faculty_id": "F202", "name": "Prof. Rahul Deshmukh",
            "department": "Computer Science",
        }
        seed_courses = [
            ("C301", "Data Structures", 4, "F201", "MON-09:00"),
            ("C302", "Database Management Systems", 4, "F202", "TUE-10:00"),
            ("C303", "Operating Systems", 4, "F202", "MON-09:00"),
            ("C304", "DevOps Fundamentals", 3, "F201", "WED-11:00"),
            ("C305", "Computer Networks", 4, "F202", "THU-09:00"),
        ]
        for cid, title, credits, fid, slot in seed_courses:
            self.courses[cid] = {
                "course_id": cid, "title": title, "credits": credits,
                "faculty_id": fid, "slot": slot, "semester": 3, "capacity": 60,
            }

    def reset(self):
        """Restore the initial state (used by tests)."""
        with self.lock:
            self.students.clear()
            self.faculty.clear()
            self.courses.clear()
            self.enrollments.clear()
            self.marks.clear()
            self._seed_initial_data()


db = Database()
