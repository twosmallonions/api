# Copyright 2025 Marius Meschter
# SPDX-License-Identifier: AGPL-3.0-only

from enum import StrEnum

from pydantic import BaseModel


class RecipeSortField(StrEnum):
    ALPHABETICAL = 'title'
    UPDATED_AT = 'updated_at'
    CREATED_AT = 'created_at'


class SortOrder(StrEnum):
    DESC = 'DESC'
    ASC = 'ASC'


class BaseSort[T](BaseModel):
    order: SortOrder
    field: T


class CursorPagination(BaseModel):
    limit: int
    cursor: str | None


class RecipeQueryParams(BaseModel):
    pagination: CursorPagination
    sort: BaseSort[RecipeSortField]
    search: str | None
