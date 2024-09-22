package com.twosmallonions.api.recipe;

import com.twosmallonions.api.recipe.dto.CreateRecipeDTO;
import com.twosmallonions.api.recipe.dto.RecipeDTO;
import org.mapstruct.Mapper;
import org.mapstruct.Mapping;
import org.mapstruct.MappingTarget;
import org.mapstruct.factory.Mappers;
import org.springframework.stereotype.Service;

@Mapper(componentModel = "spring")
public interface RecipeMapper {
    RecipeMapper INSTANCE = Mappers.getMapper(RecipeMapper.class);

    @Mapping(source = "subject", target = "subject")
    Recipe createRecipeToRecipe(CreateRecipeDTO createRecipeDTO, String subject);
    RecipeDTO recipeToRecipeDTO(Recipe recipe);
    void updateRecipeFromCreateRecipeDTO(@MappingTarget Recipe recipe, CreateRecipeDTO createRecipeDTO);
}
