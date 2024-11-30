package com.twosmallonions.api.recipe.dto;

import com.twosmallonions.api.ingredients.dto.CreateIngredientDTO;
import com.twosmallonions.api.steps.dto.CreateStepDTO;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import lombok.Builder;
import lombok.Data;
import org.hibernate.validator.constraints.URL;

import java.time.ZonedDateTime;
import java.util.List;

@Data
public class CreateRecipeDTO {
    @NotBlank
    private String title;
    private String description;
    private String servings;
    private String originalUrl;
    private int prepTime;
    private int cookTime;
    private int restTime;
    private String note;
    @URL
    private String image;

    private List<CreateIngredientDTO> ingredients;
    private List<CreateStepDTO> steps;
}
