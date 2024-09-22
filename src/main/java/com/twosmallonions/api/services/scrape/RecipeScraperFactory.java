package com.twosmallonions.api.services.scrape;

import com.twosmallonions.api.services.scrape.pyscraper.PyRecipeScraperService;
import lombok.RequiredArgsConstructor;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Component;

@Component
@RequiredArgsConstructor
public class RecipeScraperFactory {
    private final PyRecipeScraperService pyRecipeScraperService;
    private final Logger logger = LoggerFactory.getLogger(RecipeScraperFactory.class);

    public RecipeScraper getRecipeScraper() {
        logger.debug("Using pyRecipeScraperService for scraping");
        return this.pyRecipeScraperService;
    }
}
