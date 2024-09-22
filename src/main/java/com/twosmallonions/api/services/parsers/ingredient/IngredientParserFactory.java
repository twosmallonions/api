package com.twosmallonions.api.services.parsers.ingredient;

import lombok.RequiredArgsConstructor;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Component;

@Component
@RequiredArgsConstructor
public class IngredientParserFactory {
    private final SimpleIngredientParser simpleIngredientParser;
    private final Logger logger = LoggerFactory.getLogger(IngredientParserFactory.class);

    public IngredientParser getIngredientParser() {
        logger.debug("Using simple ingredient parser");
        return simpleIngredientParser;
    }
}
