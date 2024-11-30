package com.twosmallonions.api.services.scrape;

import com.twosmallonions.api.exceptions.ScraperConfigurationException;
import com.twosmallonions.api.services.scrape.pyscraper.PyRecipeScraperService;
import lombok.RequiredArgsConstructor;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Component;

import java.util.Optional;

@Component
@RequiredArgsConstructor
public class RecipeScraperFactory {
    private final Optional<PyRecipeScraperService> pyRecipeScraperService;
    private final Logger logger = LoggerFactory.getLogger(RecipeScraperFactory.class);

    public RecipeScraper getRecipeScraper() {
        logger.debug("Using pyRecipeScraperService for scraping");
        return this.pyRecipeScraperService.orElseThrow(() -> {
                logger.warn("Recipe import attempted but no scraper configured");
                return new ScraperConfigurationException("No recipe scraper has been configured");
        }
        );
    }
}
