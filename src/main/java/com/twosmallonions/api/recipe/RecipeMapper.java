package com.twosmallonions.api.recipe;

import com.twosmallonions.api.images.ImageMapper;
import com.twosmallonions.api.ingredients.IngredientsMapper;
import com.twosmallonions.api.ingredients.SortedIngredients;
import com.twosmallonions.api.recipe.dto.CreateRecipeDTO;
import com.twosmallonions.api.recipe.dto.FullRecipeDTO;
import com.twosmallonions.api.recipe.dto.RecipeDTO;
import com.twosmallonions.api.recipe.dto.UpdateRecipeDTO;
import com.twosmallonions.api.steps.StepMapper;
import lombok.NoArgsConstructor;
import lombok.RequiredArgsConstructor;
import org.mapstruct.Mapper;
import org.mapstruct.Mapping;
import org.mapstruct.MappingTarget;
import org.mapstruct.ReportingPolicy;
import org.mapstruct.factory.Mappers;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

@Mapper(
        componentModel = "spring",
        unmappedTargetPolicy = ReportingPolicy.ERROR,
        uses = {IngredientsMapper.class, StepMapper.class, ImageMapper.class}
)
@NoArgsConstructor
public abstract class RecipeMapper {
    @Autowired
    protected IngredientsMapper ingredientsMapper;

    @Autowired
    protected StepMapper stepMapper;

    @Mapping(target = "id", ignore = true)
    @Mapping(target = "slug", ignore = true)
    @Mapping(target = "added", ignore = true)
    @Mapping(target = "modified", ignore = true)
    @Mapping(target = "lastMade", ignore = true)
    @Mapping(target = "coverImage", ignore = true)
    @Mapping(target = "ingredient", ignore = true)
    @Mapping(target = "steps", ignore = true)
    @Mapping(target = "recipeImages", ignore = true)
    @Mapping(target = "totalTime", ignore = true)
    @Mapping(target = "liked", ignore = true)
    public abstract Recipe createRecipeToRecipe(CreateRecipeDTO createRecipeDTO, String subject);

    public abstract RecipeDTO recipeToRecipeDTO(Recipe recipe);

    @Mapping(target = "id", ignore = true)
    @Mapping(target = "slug", ignore = true)
    @Mapping(target = "added", ignore = true)
    @Mapping(target = "modified", ignore = true)
    @Mapping(target = "lastMade", ignore = true)
    @Mapping(target = "coverImage", ignore = true)
    @Mapping(target = "ingredient", ignore = true)
    @Mapping(target = "steps", ignore = true)
    @Mapping(target = "recipeImages", ignore = true)
    @Mapping(target = "totalTime", ignore = true)
    @Mapping(target = "subject", ignore = true)
    @Mapping(target = "image", ignore = true)
    public abstract void updateRecipeFromUpdateRecipeDTO(@MappingTarget Recipe recipe, UpdateRecipeDTO updateRecipeDTO);

    @Mapping(target = "ingredients", expression = "java(ingredientsMapper.sortedIngredientMapper(recipe.getIngredient()))")
    @Mapping(target = "steps", expression = "java(stepMapper.sortedStepMapper(recipe.getSteps()))")
    public abstract FullRecipeDTO recipeToFullRecipeDTO(Recipe recipe);

}
