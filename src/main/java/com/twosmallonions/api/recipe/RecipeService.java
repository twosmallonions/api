package com.twosmallonions.api.recipe;

import com.fasterxml.uuid.Generators;
import com.twosmallonions.api.exceptions.ResourceNotFoundException;
import com.twosmallonions.api.ingredients.*;
import com.twosmallonions.api.recipe.dto.FullRecipeDTO;
import com.twosmallonions.api.recipe.dto.IdOnly;
import com.twosmallonions.api.recipe.dto.RecipeDTO;
import com.twosmallonions.api.recipe.dto.UpdateRecipeDTO;
import com.twosmallonions.api.services.parsers.ingredient.IngredientParserFactory;
import com.twosmallonions.api.steps.*;
import com.twosmallonions.api.tags.TagService;
import lombok.RequiredArgsConstructor;
import org.apache.commons.lang3.RandomStringUtils;
import org.jetbrains.annotations.NotNull;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.*;

@RequiredArgsConstructor
@Service
public class RecipeService {
    private final RecipeRepository recipeRepository;
    private final RecipeMapper recipeMapper;
    private final UpdateIngredientsService updateIngredientsService;
    private final UpdateStepsService updateStepsService;

    @NotNull
    public List<RecipeDTO> getAllRecipes(String subject) {
        var recipes = this.recipeRepository.findBySubject(subject);
        return  recipes.stream().map(recipeMapper::recipeToRecipeDTO).toList();
    }

    @NotNull
    public RecipeDTO toggleLike(UUID id, String subject) {
        var recipe = this.getRecipe(id, subject);

        recipe.setLiked(!recipe.isLiked());

        var savedRecipe = this.recipeRepository.save(recipe);

        return recipeMapper.recipeToRecipeDTO(savedRecipe);
    }

    @NotNull
    public Recipe getRecipe(UUID id, String subject) {
        Optional<Recipe> recipe = this.recipeRepository.findByIdAndSubject(id, subject);
        if (recipe.isEmpty()) {
            throw new ResourceNotFoundException("Failed to find recipe with id " + id);
        }

        return recipe.get();
    }

    @NotNull
    public Recipe getRecipeBySlug(String slug, String subject) {
        Optional<Recipe> recipe = this.recipeRepository.findBySlugAndSubject(slug, subject);

        if (recipe.isEmpty()) {
            throw new ResourceNotFoundException("Failed to find recipe with slug " + slug);
        }

        return recipe.get();
    }


    @NotNull
    public FullRecipeDTO getFullRecipeBySlug(String slug, String subject) {
        return this.recipeMapper.recipeToFullRecipeDTO(this.getRecipeBySlug(slug, subject));
    }

    @NotNull
    public FullRecipeDTO getFullRecipe(UUID id, String subject) {
        var recipe = this.getRecipe(id, subject);
        return this.recipeMapper.recipeToFullRecipeDTO(recipe);
    }

    public boolean checkRecipeExists(UUID id, String subject) {
        Optional<IdOnly> recipe = this.recipeRepository.findByIdAndSubject(id, subject);
        return recipe.isPresent();
    }

    public void checkRecipeExistsAndThrow(UUID id, String subject) {
        if (!checkRecipeExists(id, subject)) {
            throw new ResourceNotFoundException("Failed to find recipe with id " + id);
        }
    }

    @NotNull
    @Transactional
    public Recipe createRecipe(Recipe recipe) {
        if (recipe.getId() != null) {
            throw new IllegalStateException("Trying to create an already created recipe");
        }

        if (recipe.getSlug() == null) {
            recipe.setSlug(RandomStringUtils.randomAlphanumeric(10)); // TODO: generate a proper slug
        }

        return this.recipeRepository.save(recipe);
    }

    @Transactional
    public Recipe save(Recipe recipe) {
        return this.recipeRepository.save(recipe);
    }

    @NotNull
    @Transactional
    public FullRecipeDTO updateRecipe(UUID id, String subject, UpdateRecipeDTO updateRecipeDTO) {
        var recipe = this.getRecipe(id, subject);
        var ingredientIdMapping = new HashMap<String, String>();
        this.recipeMapper.updateRecipeFromUpdateRecipeDTO(recipe, updateRecipeDTO);

        var newIngredients = updateRecipeDTO.getIngredients();
        this.updateIngredientsService.updateRecipeIngredients(recipe, newIngredients, ingredientIdMapping);

        var newSteps = updateRecipeDTO.getSteps();
        this.updateStepsService.updateRecipeSteps(recipe, newSteps, ingredientIdMapping);

        return this.recipeMapper.recipeToFullRecipeDTO(this.recipeRepository.save(recipe));
    }
}
