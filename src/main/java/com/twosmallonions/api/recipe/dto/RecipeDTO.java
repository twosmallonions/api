package com.twosmallonions.api.recipe.dto;

import com.twosmallonions.api.tags.dto.TagDTO;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.net.URI;
import java.net.URL;
import java.time.ZonedDateTime;
import java.util.HashSet;
import java.util.List;
import java.util.UUID;

@Data
@NoArgsConstructor
public class RecipeDTO {
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
    private List<URL> coverImage;
    private boolean liked;
}
