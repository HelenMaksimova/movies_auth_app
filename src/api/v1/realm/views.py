from fastapi import (
    APIRouter,
    Request,
)

from src.api.v1.realm.schemas import PublicKeyResponseSchema
from src.dependencies import DepRealmService

__all__ = ("router",)

router = APIRouter()


@router.get(
    "/token",
    response_model=PublicKeyResponseSchema,
)
async def get_public_key(
    request: Request,
    realm_service: DepRealmService,
):
    await realm_service.authenticate(request)

    if request.state.realm.keys:
        keys = request.state.realm.keys[-1]
    else:
        keys = await realm_service.create_realm_keys(
            realm_id=request.state.realm.id
        )

    return keys
