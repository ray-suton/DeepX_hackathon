from __future__ import annotations

from typing import Any

from fastapi import FastAPI, File, Form, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .errors import EstimationFailedError, PaladinError, error_payload
from .service import build_report, build_report_from_upload


app = FastAPI(title="Paladin API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5173",
        "http://localhost:5173",
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok"}


@app.exception_handler(PaladinError)
def handle_paladin_error(_: Any, exc: PaladinError) -> JSONResponse:
    return JSONResponse(content=error_payload(exc), status_code=exc.status_code)


@app.exception_handler(Exception)
def handle_unexpected_error(_: Any, exc: Exception) -> JSONResponse:
    error = EstimationFailedError(
        "An unexpected error occurred while generating the report.",
        "Try the sample model again. If the problem persists, restart the demo server.",
        {"exception": exc.__class__.__name__},
    )
    return JSONResponse(content=error_payload(error), status_code=500)


@app.post("/api/v1/report")
def create_report(payload: dict[str, Any]) -> JSONResponse:
    report = build_report(payload)
    return JSONResponse(content=report.to_dict(), status_code=200)


@app.post("/api/v1/report/upload")
async def create_report_from_upload(
    file: UploadFile = File(...),
    batch_size: int = Form(...),
    precision: str = Form("fp16"),
) -> JSONResponse:
    report = build_report_from_upload(
        filename=file.filename or "uploaded-model.onnx",
        file_bytes=await file.read(),
        batch_size=batch_size,
        precision=precision,  # type: ignore[arg-type]
    )
    return JSONResponse(content=report.to_dict(), status_code=200)


def run() -> None:
    import uvicorn

    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
