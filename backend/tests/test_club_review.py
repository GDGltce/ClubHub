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
from app.models.club import Club, ClubStatus, ClubType
from app.models.institution import College, CollegeStatus
from app.models.user import GlobalRole, User


class ClubReviewTests(unittest.TestCase):
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
        self.college_id = uuid.uuid4()
        self.pending_id = uuid.uuid4()
        self.active_id = uuid.uuid4()
        self.user = User(
            id=uuid.uuid4(),
            email="admin@example.test",
            hashed_password="not-used",
            full_name="Platform Admin",
            global_role=GlobalRole.PLATFORM_ADMIN,
        )
        self.current_role = GlobalRole.PLATFORM_ADMIN

        with self.session_factory() as db:
            db.add(
                College(
                    id=self.college_id,
                    name="Test College",
                    status=CollegeStatus.ACTIVE,
                )
            )
            db.add_all(
                [
                    Club(
                        id=self.pending_id,
                        college_id=self.college_id,
                        name="Pending Club",
                        club_type=ClubType.DEPARTMENTAL,
                        status=ClubStatus.PENDING,
                    ),
                    Club(
                        id=self.active_id,
                        college_id=self.college_id,
                        name="Active Club",
                        club_type=ClubType.DEPARTMENTAL,
                        status=ClubStatus.ACTIVE,
                    ),
                ]
            )
            db.commit()

        def override_db():
            db = self.session_factory()
            try:
                yield db
            finally:
                db.close()

        def override_current_user():
            return User(
                id=self.user.id,
                email=self.user.email,
                hashed_password=self.user.hashed_password,
                full_name=self.user.full_name,
                global_role=self.current_role,
            )

        app.dependency_overrides[get_db] = override_db
        app.dependency_overrides[get_current_user] = override_current_user
        self.client = TestClient(app)

    def tearDown(self):
        self.client.close()
        app.dependency_overrides.clear()
        with self.session_factory() as db:
            db.query(Club).delete()
            db.query(College).delete()
            db.commit()

    def test_pending_queue_is_admin_only_and_excludes_active_clubs(self):
        response = self.client.get("/api/v1/clubs/pending")
        self.assertEqual(response.status_code, 200)
        self.assertEqual([club["id"] for club in response.json()], [str(self.pending_id)])

        self.current_role = GlobalRole.STUDENT
        response = self.client.get("/api/v1/clubs/pending")
        self.assertEqual(response.status_code, 403)

    def test_admin_can_approve_or_send_back_pending_clubs(self):
        approved = self.client.patch(f"/api/v1/clubs/{self.pending_id}/approve")
        self.assertEqual(approved.status_code, 200)
        self.assertEqual(approved.json()["status"], ClubStatus.ACTIVE.value)
        public_names = [club["name"] for club in self.client.get("/api/v1/clubs").json()]
        self.assertIn("Pending Club", public_names)

        with self.session_factory() as db:
            club = Club(
                college_id=self.college_id,
                name="Needs Changes Club",
                club_type=ClubType.DEPARTMENTAL,
                status=ClubStatus.PENDING,
            )
            db.add(club)
            db.commit()
            club_id = club.id

        sent_back = self.client.patch(f"/api/v1/clubs/{club_id}/send-back")
        self.assertEqual(sent_back.status_code, 200)
        self.assertEqual(sent_back.json()["status"], ClubStatus.NEEDS_CHANGES.value)
        public_names = [club["name"] for club in self.client.get("/api/v1/clubs").json()]
        self.assertNotIn("Needs Changes Club", public_names)

    def test_review_actions_reject_non_pending_clubs(self):
        response = self.client.patch(f"/api/v1/clubs/{self.active_id}/send-back")
        self.assertEqual(response.status_code, 409)


if __name__ == "__main__":
    unittest.main()
