package com.twosmallonions.api.recipe.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import lombok.Builder;
import lombok.Data;
import org.hibernate.validator.constraints.URL;

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
    @URL
    private String image;
}
