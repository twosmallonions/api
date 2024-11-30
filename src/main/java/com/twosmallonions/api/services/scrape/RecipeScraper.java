package com.twosmallonions.api.services.scrape;

import com.twosmallonions.api.recipe.Recipe;
import com.twosmallonions.api.recipe.dto.CreateRecipeDTO;

import java.net.URI;
import java.net.URL;

public interface RecipeScraper {
    CreateRecipeDTO parse(URL uri);
}
