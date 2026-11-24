from fastapi import APIRouter, Depends, Response
from pydantic import BaseModel

from ..accounts.deps import optional_user
from ..accounts.history import record_analysis
from .model import predict

router = APIRouter(prefix="/ef-estimation", tags=["ef-estimation"])


class PredictRequest(BaseModel):
    file_url: str


@router.post("/predict")
def predict_ef(req: PredictRequest, response: Response, user=Depends(optional_user)):
    result = predict(req.file_url)
    record_analysis(user, "ef-estimation", req.file_url, result, response)
    return result
