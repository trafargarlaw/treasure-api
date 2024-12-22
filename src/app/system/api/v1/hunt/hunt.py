from fastapi import APIRouter
from pydantic import BaseModel

from src.app.system.models.hints import Hint
from src.app.system.service.hunt_service import HuntService
from src.common.enums import DirectionType
from src.common.response.response_schema import ResponseModel, response_base
from src.common.security.jwt import DependsJwtAuth

router = APIRouter()


class HintRequest(BaseModel):
    x: int
    y: int
    direction: DirectionType


@router.post('/hints', summary='Get hints', dependencies=[DependsJwtAuth])
async def get_hints(request: HintRequest) -> ResponseModel[list[Hint]]:
    hints = await HuntService.get_hints(x=request.x, y=request.y, direction=request.direction)
    return response_base.success(data=list(hints))
