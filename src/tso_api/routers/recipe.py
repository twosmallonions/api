from datetime import datetime
from uuid import UUID
from fastapi import APIRouter
from pydantic import BaseModel


class Recipe(BaseModel):
    title: str
    description: str | None = None

class RecipeCreate(Recipe):
    pass

class RecipeFull(Recipe):
    id: UUID
    owner: str
    slug: str
    created_at: datetime
    updated_at: datetime

router = APIRouter(prefix='/recipe')

@router.get('/')
async def get_all_recipes() -> RecipeFull:
    return {}