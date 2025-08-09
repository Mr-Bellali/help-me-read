"""
Analyse API endpoints for analysing the documents
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

router = APIRouter()

class AnalyzeRequest(BaseModel):
    document_content: str

@router.post(
    "/api/analyse",
    response_description="Start async analyse of the document",
    response_model=dict,
    tags=["Analyse"],
)
async def analyse_document(
    request: AnalyzeRequest
):
    """
    Start async LLM analysis of the document content using job-based processing.
    """
    if not request.document_content :
        raise HTTPException(status_code=400, detail="the document content must be provided for the analysis")

    # TODO: Implement actual analysis logic here
    return {
        "status": "success",
        "message": "Document analysis started",
        "document_length": len(request.document_content)
    }