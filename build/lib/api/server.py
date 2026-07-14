from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from api.routes import router
from api.analytics_routes import router as analytics_router

app = FastAPI(title="BugHunter API", version="0.1.0")

@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc)},
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    # Log exception internally here if logging is configured
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal pipeline error occurred"},
    )

app.include_router(router)
app.include_router(analytics_router)
