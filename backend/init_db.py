"""
Database initialization script.

Creates all tables and optionally seeds with initial data.
"""
import sys
from pathlib import Path

# Add app to path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from sqlalchemy.orm import Session
from app.core.database import engine, SessionLocal, Base
from app.models import (
    User, UserRole, TrustLevel,
    Garden, Habit, HabitCategory, HabitFrequency
)

# Import all models to ensure they're registered
from app.models import *


def create_tables():
    """Create all database tables."""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Tables created successfully!")


def seed_test_data(db: Session):
    """
    Seed database with test data.
    
    Creates a test Guardian user and sample content.
    """
    print("\nSeeding test data...")
    
    # Check if test user already exists
    test_user = db.query(User).filter(User.email == "guardian@test.com").first()
    
    if test_user:
        print("Test data already exists, skipping seed.")
        return
    
    # Create test Guardian user
    guardian = User(
        auth0_sub="auth0|test-guardian-12345",
        email="guardian@test.com",
        display_name="Test Guardian",
        bio="Test Guardian account for development",
        role=UserRole.GUARDIAN,
        trust_level=TrustLevel.FLOURISHING,
        is_verified_guide=False,
        spiritual_opt_in=False
    )
    db.add(guardian)
    db.commit()
    db.refresh(guardian)
    
    print(f"✅ Created Guardian user: {guardian.email}")
    
    # Create Garden for Guardian
    garden = Garden(
        user_id=guardian.id,
        name="Guardian's Test Garden",
        description="Test garden for development",
        is_public=True
    )
    db.add(garden)
    db.commit()
    db.refresh(garden)
    
    # Create sample habits
    habits = [
        Habit(
            garden_id=garden.id,
            name="Morning Meditation",
            description="10 minutes of mindfulness",
            category=HabitCategory.SPIRITUAL,
            frequency=HabitFrequency.DAILY,
            target_count=1
        ),
        Habit(
            garden_id=garden.id,
            name="Exercise",
            description="30 minutes of physical activity",
            category=HabitCategory.PHYSICAL,
            frequency=HabitFrequency.DAILY,
            target_count=1
        ),
        Habit(
            garden_id=garden.id,
            name="Reading",
            description="Read for at least 20 minutes",
            category=HabitCategory.MENTAL,
            frequency=HabitFrequency.DAILY,
            target_count=1
        )
    ]
    
    for habit in habits:
        db.add(habit)
    
    db.commit()
    
    print(f"✅ Created {len(habits)} sample habits")
    print("\n🌱 Test data seeded successfully!")
    print(f"\nTest Guardian credentials:")
    print(f"  Email: {guardian.email}")
    print(f"  Auth0 Sub: {guardian.auth0_sub}")
    print(f"  Role: {guardian.role.value}")
    print(f"  Trust Level: {guardian.trust_level.value}")


def main():
    """Main initialization function."""
    print("=" * 60)
    print("Garden Platform - Database Initialization")
    print("=" * 60)
    
    # Create tables
    create_tables()
    
    # Ask if user wants to seed test data
    seed = input("\nSeed database with test data? (y/n): ").lower().strip()
    
    if seed == 'y':
        db = SessionLocal()
        try:
            seed_test_data(db)
        except Exception as e:
            print(f"\n❌ Error seeding data: {e}")
            db.rollback()
        finally:
            db.close()
    else:
        print("\nSkipping test data seed.")
    
    print("\n✅ Database initialization complete!")
    print("\nNext steps:")
    print("  1. Update .env with your Auth0 credentials")
    print("  2. Run: uvicorn app.main:app --reload")
    print("  3. Visit: http://localhost:8000/docs")


if __name__ == "__main__":
    main()
