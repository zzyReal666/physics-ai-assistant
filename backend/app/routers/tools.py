from fastapi import APIRouter

router = APIRouter()


@router.get('/ping', summary='工具模块占位')
async def tools_ping() -> dict:
    return {'message': 'tools router placeholder'}
