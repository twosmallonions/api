package com.twosmallonions.api.recipeimport;

import com.twosmallonions.api.recipe.Recipe;
import com.twosmallonions.api.recipe.RecipeMapper;
import com.twosmallonions.api.recipe.RecipeRepository;
import com.twosmallonions.api.recipe.RecipeService;
import com.twosmallonions.api.services.scrape.RecipeScraperFactory;
import lombok.RequiredArgsConstructor;
import org.apache.commons.lang3.RandomStringUtils;
import org.springframework.security.oauth2.server.resource.authentication.JwtAuthenticationToken;
import org.springframework.stereotype.Service;

import java.net.URI;
import java.net.URL;

@Service
@RequiredArgsConstructor
public class RecipeImportService {
    private final RecipeScraperFactory recipeScraperFactory;
    private final RecipeMapper recipeMapper;
    private final RecipeService recipeService;

    public Recipe importRecipeFromUrl(URL uri, String subject) {
        var scraper = recipeScraperFactory.getRecipeScraper();
        var createRecipeDTO = scraper.parse(uri);
        var recipe = this.recipeMapper.createRecipeToRecipe(createRecipeDTO, subject);

        return this.recipeService.createRecipe(recipe);
    }
}
