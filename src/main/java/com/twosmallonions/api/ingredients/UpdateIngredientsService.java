package com.twosmallonions.api.ingredients;

import com.fasterxml.uuid.Generators;
import com.twosmallonions.api.ingredients.dto.IngredientDTO;
import com.twosmallonions.api.recipe.Recipe;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.HashMap;
import java.util.List;
import java.util.UUID;

@Service
@RequiredArgsConstructor
public class UpdateIngredientsService {
    private final IngredientsRepository ingredientsRepository;
    private final IngredientsMapper ingredientsMapper;
    @Transactional
    public void updateRecipeIngredients(Recipe recipe, List<IngredientDTO> newIngredients, HashMap<String, String> ingredientIdMapping) {
        recipe.removeAllIngredients();
        for (int orderIdx = 0; orderIdx < newIngredients.size(); orderIdx++) {
            var ingredientDTO = newIngredients.get(orderIdx);
            var oldId = ingredientDTO.getId();
            var ingredient = this.updateOrCreateIngredient(ingredientDTO);
            ingredientIdMapping.put(oldId, ingredient.getId().toString());
            ingredient.setOrderIdx(orderIdx);
            recipe.addIngredient(ingredient);
        }
    }

    @Transactional
    protected Ingredient updateOrCreateIngredient(IngredientDTO ingredientDTO) {
        Ingredient ingredient;
        try {
            var ingredientUUID  = UUID.fromString(ingredientDTO.getId());
            var tmpIngredient = this.ingredientsRepository.findById(ingredientUUID);
            if (tmpIngredient.isEmpty()) {
                ingredient = this.ingredientsMapper.ingredientDTOToIngredient(ingredientDTO, 0);
            } else {
                ingredient = tmpIngredient.get();
                this.ingredientsMapper.updateIngredient(ingredient, ingredientDTO);
            }
        } catch (IllegalArgumentException e) {
            // we have a new ingredient
            ingredientDTO.setId(Generators.timeBasedEpochGenerator().generate().toString());
            ingredient = this.ingredientsMapper.ingredientDTOToIngredient(ingredientDTO, 0);
        }

        return ingredient;
    }
}
