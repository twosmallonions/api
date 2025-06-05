# Copyright 2025 Marius Meschter
# SPDX-License-Identifier: AGPL-3.0-only


import random
import string
import uuid
from collections.abc import Callable

import pytest

from tso_api.models.recipe import RecipeCreate, RecipeUpdate


@pytest.fixture
def recipe_create(recipe_create_fn: Callable[[], RecipeCreate]) -> RecipeCreate:
    return recipe_create_fn()


@pytest.fixture
def recipe_create_fn(ascii_letter_string: Callable[[int], str]) -> Callable[[], RecipeCreate]:
    def __run() -> RecipeCreate:
        return RecipeCreate(
            title=ascii_letter_string(7),
            note=ascii_letter_string(50),
            cook_time=random.randint(0, 80),
            prep_time=random.randint(0, 80),
            recipe_yield=ascii_letter_string(5),
            collection=uuid.uuid4(),
        )

    return __run


@pytest.fixture
def recipe_update():
    updated_title = 'updated_title'
    updated_description = 'updated description'
    updated_cook_time = 500
    updated_prep_time = 500
    updated_recipe_yield = str(10)
    updated_liked = True

    return RecipeUpdate(
        title=updated_title,
        note=updated_description,
        cook_time=updated_cook_time,
        prep_time=updated_prep_time,
        recipe_yield=str(updated_recipe_yield),
        liked=updated_liked,
        collection=uuid.uuid4(),
    )


@pytest.fixture
def ascii_letter_string() -> Callable[[int], str]:
    return lambda n: ''.join(random.choices(string.ascii_letters, k=n))
