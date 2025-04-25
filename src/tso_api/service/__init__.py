# Copyright 2025 Marius Meschter
# SPDX-License-Identifier: AGPL-3.0-only

from tso_api.db import db_pool
from tso_api.service.collection_service import CollectionService
from tso_api.service.recipe_asset import RecipeAssetService
from tso_api.service.recipe_service import RecipeService
from tso_api.service.user_service import UserService

collection_service = CollectionService(db_pool)
recipe_service = RecipeService(db_pool)
user_service = UserService(db_pool)
recipe_asset_service = RecipeAssetService(db_pool)
