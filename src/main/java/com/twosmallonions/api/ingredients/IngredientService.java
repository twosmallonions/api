package com.twosmallonions.api.ingredients;

import com.fasterxml.uuid.Generators;
import com.twosmallonions.api.ingredients.dto.CreateIngredientDTO;
import com.twosmallonions.api.ingredients.dto.IngredientDTO;
import com.twosmallonions.api.recipe.Recipe;
import com.twosmallonions.api.recipe.RecipeService;
import com.twosmallonions.api.services.parsers.ingredient.IngredientParserFactory;
import lombok.RequiredArgsConstructor;
import org.jetbrains.annotations.NotNull;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.UUID;

@Service
@RequiredArgsConstructor
public class IngredientService {
    private final RecipeService recipeService;
    private final IngredientParserFactory ingredientParserFactory;
    private final IngredientsMapper ingredientsMapper;
    private final IngredientsRepository ingredientsRepository;
    @NotNull
    @Transactional
    public List<Ingredient> addIngredientToRecipe(UUID id, String subject, CreateIngredientDTO createIngredientDTO) {
        var recipe = this.recipeService.getRecipe(id, subject);

        var createIngredientDTOParsed = this.ingredientParserFactory.getIngredientParser().parse(createIngredientDTO);
        var ingredient = this.ingredientsMapper.createIngredientDTOToIngredient(
                createIngredientDTOParsed,
                recipe.getIngredient().size()
        );
        recipe.addIngredient(ingredient);

        this.ingredientsRepository.save(ingredient);
        return recipe.getIngredient();
    }

    @NotNull
    public List<Ingredient> getIngredientsFromRecipe(UUID id, String subject) {
        var recipe = this.recipeService.getRecipe(id, subject);

        return recipe.getIngredient();
    }

}
