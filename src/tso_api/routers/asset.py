from uuid import UUID
from fastapi import APIRouter
from fastapi.responses import FileResponse

from tso_api.dependency import GetUser
from tso_api.service import recipe_asset_service


router = APIRouter(prefix='/api/asset')

@router.get('/{collection_id}/{asset_id}')
async def get_asset(user: GetUser, collection_id: UUID, asset_id: UUID) -> FileResponse:
    asset = await recipe_asset_service.get_asset(collection_id, asset_id, user)

    return FileResponse(asset.path)
