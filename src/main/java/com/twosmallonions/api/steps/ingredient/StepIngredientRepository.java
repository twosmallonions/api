package com.twosmallonions.api.steps.ingredient;

import com.twosmallonions.api.ingredients.Ingredient;
import org.springframework.data.repository.CrudRepository;

import java.util.UUID;

public interface StepIngredientRepository extends CrudRepository<StepIngredient, UUID> {
}