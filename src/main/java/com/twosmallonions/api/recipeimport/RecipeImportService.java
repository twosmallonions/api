package com.twosmallonions.api.recipeimport;

import com.twosmallonions.api.recipe.Recipe;
import com.twosmallonions.api.recipe.RecipeRepository;
import com.twosmallonions.api.services.scrape.RecipeScraperFactory;
import lombok.RequiredArgsConstructor;
import org.apache.commons.lang3.RandomStringUtils;
import org.springframework.security.oauth2.server.resource.authentication.JwtAuthenticationToken;
import org.springframework.stereotype.Service;

import java.net.URI;

@Service
@RequiredArgsConstructor
public class RecipeImportService {
    private final RecipeScraperFactory recipeScraperFactory;
    private final RecipeRepository recipeRepository;

    public Recipe importRecipeFromUrl(URI uri, String subject) {
        var scraper = recipeScraperFactory.getRecipeScraper();
        var recipe = scraper.parse(uri);
        recipe.setSubject(subject);
        // FIXME
        recipe.setSlug(RandomStringUtils.randomAlphanumeric(9));

        return this.recipeRepository.save(recipe);
    }
}
