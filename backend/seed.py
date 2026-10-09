"""
Seed script: creates default platform admin and a sample college+club for demo
Run: python seed.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.db.session import SessionLocal, engine
import app.db.base  # ensure all models are loaded
from app.db.session import Base
from app.models.user import User, UserProfile, GlobalRole
from app.models.institution import College, CollegeStatus
from app.models.club import Club, ClubType, ClubStatus
from app.core.security import hash_password


def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        # Admin
        if not db.query(User).filter(User.email == "admin@clubhub.dev").first():
            admin = User(
                email="admin@clubhub.dev",
                hashed_password=hash_password("admin1234"),
                full_name="Platform Admin",
                global_role=GlobalRole.PLATFORM_ADMIN,
                is_active=True,
                is_verified=True,
            )
            db.add(admin)
            db.flush()
            db.add(UserProfile(user_id=admin.id))

        # Sample college
        college = db.query(College).filter(College.short_name == "DEMO").first()
        if not college:
            college = College(
                name="Demo Engineering College",
                short_name="DEMO",
                city="Mumbai",
                state="Maharashtra",
                status=CollegeStatus.ACTIVE,
            )
            db.add(college)
            db.flush()

        # Sample club
        if not db.query(Club).filter(Club.name == "GDG On Campus DEMO").first():
            club = Club(
                college_id=college.id,
                name="GDG On Campus DEMO",
                short_name="GDG",
                description="Google Developer Group On Campus – Demo Club",
                club_type=ClubType.INSTITUTE_LEVEL,
                status=ClubStatus.ACTIVE,
                is_public=True,
            )
            db.add(club)

        db.commit()
        print("Seed complete.")
        print("Admin: admin@clubhub.dev / admin1234")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
