from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response

from app.schemas.qr import QRCodeRequest, QRCodeResponse
from app.services.qr_service import QRService

router = APIRouter(prefix="/api")


def get_qr_service() -> QRService:
    raise NotImplementedError(
        "QRService dependency must be overridden at app startup"
    )


@router.post("/generate", response_model=QRCodeResponse, status_code=201)
async def generate_qr(
    request: QRCodeRequest,
    service: QRService = Depends(get_qr_service),
) -> QRCodeResponse:
    return await service.generate(url=str(request.url), format=request.format)


@router.get("/history", response_model=list[QRCodeResponse])
async def get_history(
    limit: int = 50,
    offset: int = 0,
    service: QRService = Depends(get_qr_service),
) -> list[QRCodeResponse]:
    return await service.list_history(limit=limit, offset=offset)


@router.get("/qr/{id}", response_model=QRCodeResponse)
async def get_qr(
    id: UUID,
    service: QRService = Depends(get_qr_service),
) -> QRCodeResponse:
    result = await service.get_by_id(id)
    if not result:
        raise HTTPException(status_code=404, detail="QR code not found")
    return result


@router.delete("/qr/{id}", status_code=204)
async def delete_qr(
    id: UUID,
    service: QRService = Depends(get_qr_service),
) -> Response:
    deleted = await service.delete(id)
    if not deleted:
        raise HTTPException(status_code=404, detail="QR code not found")
    return Response(status_code=204)
