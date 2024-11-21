package com.twosmallonions.api.services.scrape;

import com.twosmallonions.api.recipe.Recipe;

import java.net.URI;

public interface RecipeScraper {
    Recipe parse(URI uri);
}
