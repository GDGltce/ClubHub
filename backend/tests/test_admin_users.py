import sys
import unittest
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import app.db.base  # noqa: F401
from app.api.deps import get_current_user
from app.db.session import Base, get_db
from app.main import app
from app.models.user import GlobalRole, User


class AdminUsersTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = create_engine(
            "sqlite://",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        cls.session_factory = sessionmaker(bind=cls.engine)
        Base.metadata.create_all(cls.engine)

    @classmethod
    def tearDownClass(cls):
        Base.metadata.drop_all(cls.engine)
        cls.engine.dispose()

    def setUp(self):
        self.admin_id = uuid.uuid4()
        self.student_id = uuid.uuid4()
        self.coordinator_id = uuid.uuid4()
        self.current_role = GlobalRole.PLATFORM_ADMIN

        with self.session_factory() as db:
            db.add_all([
                User(
                    id=self.admin_id,
                    email="admin@campus.edu",
                    hashed_password="not-used",
                    full_name="Platform Admin",
                    global_role=GlobalRole.PLATFORM_ADMIN,
                    is_active=True,
                ),
                User(
                    id=self.student_id,
                    email="student@campus.edu",
                    hashed_password="not-used",
                    full_name="Alice Student",
                    global_role=GlobalRole.STUDENT,
                    is_active=True,
                ),
                User(
                    id=self.coordinator_id,
                    email="coordinator@campus.edu",
                    hashed_password="not-used",
                    full_name="Prof. Coordinator",
                    global_role=GlobalRole.FACULTY_COORDINATOR,
                    is_active=False,
                ),
            ])
            db.commit()

        def override_db():
            db = self.session_factory()
            try:
                yield db
            finally:
                db.close()

        def override_current_user():
            if self.current_role == GlobalRole.PLATFORM_ADMIN:
                return User(
                    id=self.admin_id,
                    email="admin@campus.edu",
                    hashed_password="not-used",
                    full_name="Platform Admin",
                    global_role=GlobalRole.PLATFORM_ADMIN,
                    is_active=True,
                )
            return User(
                id=self.student_id,
                email="student@campus.edu",
                hashed_password="not-used",
                full_name="Alice Student",
                global_role=GlobalRole.STUDENT,
                is_active=True,
            )

        app.dependency_overrides[get_db] = override_db
        app.dependency_overrides[get_current_user] = override_current_user
        self.client = TestClient(app)

    def tearDown(self):
        self.client.close()
        app.dependency_overrides.clear()
        with self.session_factory() as db:
            db.query(User).delete()
            db.commit()

    def test_users_endpoint_requires_admin_role(self):
        self.current_role = GlobalRole.STUDENT
        response = self.client.get("/api/v1/users")
        self.assertEqual(response.status_code, 403)

    def test_admin_can_list_all_accounts_with_roles_and_active_status(self):
        response = self.client.get("/api/v1/users")
        self.assertEqual(response.status_code, 200)
        users = response.json()
        self.assertEqual(len(users), 3)

        emails = {u["email"]: u for u in users}
        self.assertIn("admin@campus.edu", emails)
        self.assertEqual(emails["admin@campus.edu"]["global_role"], GlobalRole.PLATFORM_ADMIN.value)
        self.assertTrue(emails["admin@campus.edu"]["is_active"])

        self.assertIn("student@campus.edu", emails)
        self.assertEqual(emails["student@campus.edu"]["global_role"], GlobalRole.STUDENT.value)
        self.assertTrue(emails["student@campus.edu"]["is_active"])

        self.assertIn("coordinator@campus.edu", emails)
        self.assertEqual(emails["coordinator@campus.edu"]["global_role"], GlobalRole.FACULTY_COORDINATOR.value)
        self.assertFalse(emails["coordinator@campus.edu"]["is_active"])

    def test_admin_can_filter_by_role_and_active(self):
        # Filter by role
        response = self.client.get(f"/api/v1/users?role={GlobalRole.STUDENT.value}")
        self.assertEqual(response.status_code, 200)
        users = response.json()
        self.assertEqual(len(users), 1)
        self.assertEqual(users[0]["email"], "student@campus.edu")

        # Filter by inactive
        response = self.client.get("/api/v1/users?active=false")
        self.assertEqual(response.status_code, 200)
        users = response.json()
        self.assertEqual(len(users), 1)
        self.assertEqual(users[0]["email"], "coordinator@campus.edu")

    def test_admin_can_update_user_status_and_role(self):
        # Deactivate student
        response = self.client.patch(
            f"/api/v1/users/{self.student_id}",
            json={"is_active": False},
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.json()["is_active"])

        # Change role to faculty coordinator
        response = self.client.patch(
            f"/api/v1/users/{self.student_id}",
            json={"global_role": GlobalRole.FACULTY_COORDINATOR.value},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["global_role"], GlobalRole.FACULTY_COORDINATOR.value)

    def test_admin_cannot_deactivate_or_demote_themselves(self):
        # Cannot deactivate own account
        response = self.client.patch(
            f"/api/v1/users/{self.admin_id}",
            json={"is_active": False},
        )
        self.assertEqual(response.status_code, 400)

        # Cannot demote own account
        response = self.client.patch(
            f"/api/v1/users/{self.admin_id}",
            json={"global_role": GlobalRole.STUDENT.value},
        )
        self.assertEqual(response.status_code, 400)


if __name__ == "__main__":
    unittest.main()
