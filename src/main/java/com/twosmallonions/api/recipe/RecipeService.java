package com.twosmallonions.api.recipe;

import com.twosmallonions.api.exceptions.ResourceNotFoundException;
import com.twosmallonions.api.ingredients.Ingredients;
import com.twosmallonions.api.ingredients.IngredientsMapper;
import com.twosmallonions.api.ingredients.IngredientsRepository;
import com.twosmallonions.api.ingredients.dto.CreateIngredientDTO;
import com.twosmallonions.api.ingredients.dto.IngredientDTO;
import com.twosmallonions.api.recipe.dto.CreateRecipeDTO;
import jakarta.persistence.EntityManager;
import lombok.RequiredArgsConstructor;
import org.apache.commons.lang3.RandomStringUtils;
import org.jetbrains.annotations.NotNull;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.ArrayList;
import java.util.UUID;

@RequiredArgsConstructor
@Service
public class RecipeService {
    private final RecipeRepository recipeRepository;
    private final RecipeMapper recipeMapper;
    private final IngredientsMapper ingredientsMapper;

    @NotNull
    public Recipe getRecipe(long id, String subject) {
        var recipe = this.recipeRepository.findByIdAndSubject(id, subject);
        if (recipe.isEmpty()) {
            throw new ResourceNotFoundException();
        }

        return recipe.get();
    }

    @NotNull
    @Transactional
    public Recipe saveRecipe(Recipe recipe) {
        if (recipe.getSlug() == null) {
            recipe.setSlug(RandomStringUtils.randomAlphanumeric(10));
        }

        return this.recipeRepository.save(recipe);
    }

    @NotNull
    @Transactional
    public Ingredients addIngredientToRecipe(long recipeId, String subject, CreateIngredientDTO createIngredientDTO) {
        var recipe = this.getRecipe(recipeId, subject);
        Ingredients ingredients;

        if (recipe.getIngredients() == null) {
            ingredients = new Ingredients();
            recipe.setIngredients(ingredients);
        } else {
            ingredients = recipe.getIngredients();
        }

        var ingredientDTO = this.ingredientsMapper.createIngredientDTOToIngredientDTO(createIngredientDTO, UUID.randomUUID());
        ingredients.getIngredients().add(ingredientDTO);
        return recipeRepository.save(recipe).getIngredients();
    }

    @NotNull
    public ArrayList<IngredientDTO> getIngredientsFromRecipe(long recipeId, String subject) {
        var recipe = this.getRecipe(recipeId, subject);

        if (recipe.getIngredients() == null) {
            return new ArrayList<>();
        }

        return recipe.getIngredients().getIngredients();
    }

    public Recipe updateRecipe(long recipeId, String subject, CreateRecipeDTO createRecipeDTO) {
        var recipe = this.getRecipe(recipeId, subject);

        this.recipeMapper.updateRecipeFromCreateRecipeDTO(recipe, createRecipeDTO);

        return this.recipeRepository.save(recipe);
    }
}
