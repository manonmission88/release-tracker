import logging
import time

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError

from .config import configure_logging, get_settings
from .routers import auth, projects, tasks

# logging.basiscConfig(level = loggingInfo)
# When your application runs,
# you need a way to know what requests arrived, what operations succeeded, and why something failed.
configure_logging(debug=get_settings().debug)
logger = logging.getLogger(__name__)
"""
Loggers use severity levels to filter messages. The standard levels, in increasing order of severity:

DEBUG: Detailed diagnostic information.
INFO: General operational events.
WARNING: Something unexpected happened, but the application is still running.
ERROR: A serious problem occurred, and a specific operation failed.
CRITICAL: A fatal error that may cause the application to crash.


"""

logger.debug("Parsing request payload")
logger.info("Project Created Succesfully")
logger.warning("Rate Limit Approaching")

app = FastAPI(
    title="Release Tracker API",
    description="An API for tracking project milestones and developer tasks",
)

app.include_router(projects.router)
app.include_router(tasks.router)
app.include_router(auth.router)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.perf_counter()
    response = await call_next(request)
    process_time = (time.perf_counter() - start_time) * 1000

    logger.info(
        "%s %s completed in %.2fms with status code %s",
        request.method,
        request.url.path,
        process_time,
        response.status_code,
    )
    return response


# @app.middleware("http")
# async def my_middleware(request: Request, call_next):
#     # pre route work goes here
#     # BEFORE THe endpoint is called
#     response = await call_next(request)
#     #post route work goes here
#     # AFTER THE ENDPOINT FINISHED
#     return response


# Declare a reusable requirement:
# "This endpoint needs a database session."
# Expose a public endpoint that returns ProjectRead objects.
"""
By specifying response_model=list[ProjectRead], FastAPI automatically takes the Project database models returned by session.exec(), validates them against our ProjectRead schema, and serializes them to JSON.
We don't have to map the fields ourselves.

"""

"""
FastAPI's @app.exception_handler() decorator solves both problems.
It registers a function that runs whenever a specific exception type bubbles up out of a route, dependency, or anywhere else inside a request.
Routes stay focused on the happy path, crud.py stays free of HTTP knowledge, and the conversion to a 409 happens in one place.

"""


@app.exception_handler(IntegrityError)
def handle_integrity_error(request: Request, exc: IntegrityError):
    # Additional note:
    # This currently treats every IntegrityError as a conflict.
    # In production, distinguish unique violations from other
    # database constraint failures.
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"detail": "Data Conflict occured (e.g Duplicate Entry)"},
    )


# our project model requires unique slug -> that we will use as part of the URL
# helper function to create the unique slug
"""
In production, use a library like python-slugify to handle special cases like unicode and more.
You'll also need to validate the slug doesn't already exist when updating and creating Project

"""


# root route ("/")
@app.get("/")
def read_root() -> dict[str, str]:
    # logger.info("TEST LOG: ROOT")
    return {"app": "Release Tracker API", "docs": "/docs", "health": "/health"}
