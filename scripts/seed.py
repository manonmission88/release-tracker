from sqlmodel import Session

from release_tracker.database import get_engine
from release_tracker.models import Project


def seed() -> None:
    """
    Insert three sample projects into the database.

    This function is useful for setting up sample data
    during development and testing.
    """

    # Step 1: Create a database session using the engine.
    # The context manager closes the session afterward.
    with Session(get_engine()) as session:
        # Step 2: Create three Project model instances.
        # At this point, they are Python objects,
        # not yet saved in the database.

        frontend = Project(name="Frontend Redesign", slug="frontend-redesign")

        api = Project(name="Payments API", slug="payments-api")

        dashboard = Project(name="Internal Dashboard", slug="internal-dashboard")

        # Step 3: Add the objects to the session.
        # This marks them for insertion.
        session.add(frontend)
        session.add(api)
        session.add(dashboard)

        # Step 4: Commit the transaction.
        # SQLAlchemy flushes pending INSERT operations
        # and commits the changes to the database.
        session.commit()

        print("Loaded sample data for the three projects")


# Step 5: Run seed() only when this module
# is executed directly as a Python program.
if __name__ == "__main__":
    seed()
