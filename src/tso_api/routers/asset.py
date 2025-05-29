from uuid import UUID

from fastapi import APIRouter, Response
from fastapi.responses import FileResponse

from tso_api.dependency import GetUser, RecipeAssetServiceDep

router = APIRouter(prefix='/api/asset')


@router.get('/{collection_id}/{asset_id}')
async def get_asset(
    user: GetUser, collection_id: UUID, asset_id: UUID, recipe_asset_service: RecipeAssetServiceDep, response: Response
) -> FileResponse:
    asset = await recipe_asset_service.get_asset(collection_id, asset_id, user)
    return FileResponse(asset.path, headers={'cache-control': 'private, max-age=31536000'})