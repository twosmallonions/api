package com.twosmallonions.api.ingredients;

import com.twosmallonions.api.recipe.Recipe;
import org.springframework.data.repository.CrudRepository;

import java.util.Optional;
import java.util.UUID;

public interface IngredientsRepository extends CrudRepository<Ingredient, UUID> {
    Optional<Ingredient> findByIdAndRecipe(UUID id, Recipe recipe);
}
