package com.twosmallonions.api.services.parsers.ingredient;

import com.twosmallonions.api.ingredients.dto.CreateIngredientDTO;

public interface IngredientParser {
    CreateIngredientDTO parse(String input);
    default CreateIngredientDTO parse(CreateIngredientDTO input) {
        return this.parse(input.getNotes());
    }
}
