package com.twosmallonions.api.services.scrape.pyscraper.response;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.Data;

@Data
public class RecipeNutrients {
    private String calories;
    @JsonProperty("carbohydrateContent")
    private String carbohydrateContent;
    @JsonProperty("proteinContent")
    private String proteinContent;
    @JsonProperty("fatContent")
    private String fatContent;
    @JsonProperty("saturatedFatContent")
    private String saturatedFatContent;
    @JsonProperty("cholesterolContent")
    private String cholesterolContent;
    @JsonProperty("sodiumContent")
    private String sodiumContent;
    @JsonProperty("fiberContent")
    private String fiberContent;
    @JsonProperty("sugarContent")
    private String sugarContent;
    @JsonProperty("unsaturatedFatContent")
    private String unsaturatedFatContent;
    @JsonProperty("servingSize")
    private String servingSize;

    // Getters and setters omitted for brevity
}
