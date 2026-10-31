from datetime import UTC, datetime

from fastapi import FastAPI, HTTPException, status

from .models import ProjectRead


app = FastAPI(title = "Release Tracker API")
_seed_time  = datetime(2026,1,1,tzinfo=UTC)

mock_database: dict[int, ProjectRead] = {
    1: ProjectRead(
        id=1,
        name="Frontend Redesign",
        slug="frontend-redesign",
        created_at=_seed_time,
    ),
    2: ProjectRead(id=2, name="API v2", slug="api-v2", created_at=_seed_time),
    3: ProjectRead(
        id=3,
        name="Database Migration",
        slug="database-migration",
        created_at=_seed_time,
    ),
}
@app.get("/projects")
def list_projects()-> list[dict]:
    return [{"id":1,"name":"EXAMPLE"}]
