package com.twosmallonions.api.recipe.dto;

import com.twosmallonions.api.ingredients.dto.IngredientDTO;
import com.twosmallonions.api.steps.dto.StepDTO;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.net.URL;
import java.time.ZonedDateTime;
import java.util.List;
import java.util.UUID;

@Data
@NoArgsConstructor
public class FullRecipeDTO {
    private String subject;
    private String slug;
    private String title;
    private String description;
    private String servings;
    private String originalUrl;
    private ZonedDateTime added;
    private ZonedDateTime modified;
    private int prepTime;
    private int cookTime;
    private int restTime;
    private int totalTime;
    private String note;
    private String image;
    private UUID id;
    private List<IngredientDTO> ingredients;
    private List<StepDTO> steps;
    private List<URL> coverImage;
}
