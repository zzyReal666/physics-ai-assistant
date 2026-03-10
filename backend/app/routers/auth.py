from fastapi import APIRouter

router = APIRouter()


@router.get('/ping', summary='认证模块占位')
async def auth_ping() -> dict:
    return {'message': 'auth router placeholder'}
