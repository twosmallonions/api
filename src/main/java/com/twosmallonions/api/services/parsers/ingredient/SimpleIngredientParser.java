package com.twosmallonions.api.services.parsers.ingredient;

import com.twosmallonions.api.ingredients.IngredientsMapper;
import com.twosmallonions.api.ingredients.dto.CreateIngredientDTO;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

@Service
@RequiredArgsConstructor
public class SimpleIngredientParser implements IngredientParser {
    private final IngredientsMapper ingredientsMapper;
    @Override
    public CreateIngredientDTO parse(String input) {
        var createIngredientDto = new CreateIngredientDTO();
        createIngredientDto.setNotes(input);

        return createIngredientDto;
    }

    @Override
    public CreateIngredientDTO parse(CreateIngredientDTO createIngredientDTO) {
        return createIngredientDTO;
    }
}
