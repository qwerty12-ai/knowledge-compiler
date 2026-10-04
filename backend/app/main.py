from fastapi import FastAPI

app = FastAPI(
    title="Knowledge Compiler API",
    description="API for analyzing repositories and inspecting engineering knowledge.",
    version="0.1.0"
)

@app.get("/", include_in_schema=False)
def root() -> dict:
    return {
        "name": "Knowledge Compiler API",
        "version": app.version,
        "description": (
            "Turn codebases into structured engineering knowledge "
            "backed by evidence."
        ),
        "status": "running",
        "links": {
            "documentation": "/docs",
            "openapi_schema": "/openapi.json",
            "health": "/health"
        },
        "capabilities": [
            "Repository discovery",
            "Evidence extraction",
            "Claim generation",
            "Evidence-backend investigation"
        ],
        "message": (
            "Welcome to Knowledge Compiler."
            " Explore the API documentation to get started."
        )
    }

@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}