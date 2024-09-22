package com.twosmallonions.api.recipe.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.ZonedDateTime;
import java.util.UUID;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class RecipeDTO {
    private long id;
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
    private UUID uuid;
}
