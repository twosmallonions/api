package com.twosmallonions.api.recipe.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import lombok.Builder;
import lombok.Data;

import java.time.ZonedDateTime;

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
    private String image;
}
