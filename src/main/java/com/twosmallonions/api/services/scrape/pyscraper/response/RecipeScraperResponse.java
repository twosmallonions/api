package com.twosmallonions.api.services.scrape.pyscraper.response;

import com.fasterxml.jackson.annotation.JsonProperty;
import com.twosmallonions.api.ingredients.Ingredient;
import com.twosmallonions.api.ingredients.dto.IngredientDTO;
import com.twosmallonions.api.recipe.Recipe;
import com.twosmallonions.api.steps.Step;
import com.twosmallonions.api.steps.dto.StepDTO;
import lombok.Data;

import java.util.ArrayList;
import java.util.List;
import java.util.UUID;
import java.util.stream.Collectors;
import java.util.stream.IntStream;

@Data
public class RecipeScraperResponse {
    private String author;
    @JsonProperty("canonical_url")
    private String canonicalUrl;
    private String category;
    @JsonProperty("cook_time")
    private int cookTime;
    private String cuisine;
    private String description;
    private String host;
    private String image;
    @JsonProperty("ingredient_groups")
    private List<IngredientGroup> ingredientGroups;
    private List<String> ingredients;
    private String instructions;
    @JsonProperty("instructions_list")
    private List<String> instructionsList;
    private List<String> keywords;
    private String language;
    private RecipeNutrients nutrients;
    @JsonProperty("prep_time")
    private int prepTime;
    private double ratings;
    @JsonProperty("ratings_count")
    private int ratingsCount;
    @JsonProperty("site_name")
    private String siteName;
    private String title;
    @JsonProperty("total_time")
    private int totalTime;
    private String yields;

    public Recipe toRecipe() {
        var recipe = new Recipe();
        recipe.setTitle(this.title);
        recipe.setDescription(this.description);
        recipe.setServings(this.yields);
        recipe.setOriginalUrl(this.canonicalUrl);
        recipe.setPrepTime(this.prepTime);
        recipe.setCookTime(this.cookTime);

        IntStream.range(0, this.ingredients.size())
                .forEach(i -> {
                    var ingredient = new Ingredient();
                    ingredient.setNotes(this.ingredients.get(i));
                    ingredient.setOrderIdx(i);

                    recipe.addIngredient(ingredient);
                });

        IntStream.range(0, this.instructionsList.size())
                .forEach(i -> {
                    var step = new Step();
                    step.setDescription(this.instructionsList.get(i));
                    step.setOrder_idx(i);

                    recipe.addStep(step);
                });

        return recipe;
    }
}

