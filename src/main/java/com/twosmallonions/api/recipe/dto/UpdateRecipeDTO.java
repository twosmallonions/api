package com.twosmallonions.api.recipe.dto;

import com.twosmallonions.api.ingredients.dto.IngredientDTO;
import com.twosmallonions.api.steps.dto.StepDTO;
import jakarta.validation.constraints.NotBlank;
import lombok.Data;
import org.hibernate.validator.constraints.URL;

import java.util.List;

@Data
public class UpdateRecipeDTO {
    @NotBlank
    private String title;
    private String description;
    private String servings;
    private String originalUrl;
    private int prepTime;
    private int cookTime;
    private int restTime;
    private String note;

    private List<IngredientDTO> ingredients;
    private List<StepDTO> steps;
    private boolean liked;

}
