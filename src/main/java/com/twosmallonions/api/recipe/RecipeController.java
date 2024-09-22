package com.twosmallonions.api.recipe;

import com.twosmallonions.api.ingredients.dto.CreateIngredientDTO;
import com.twosmallonions.api.ingredients.dto.IngredientDTO;
import com.twosmallonions.api.recipe.dto.CreateRecipeDTO;
import com.twosmallonions.api.recipe.dto.RecipeDTO;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.http.ResponseEntity;
import org.springframework.security.oauth2.server.resource.authentication.JwtAuthenticationToken;
import org.springframework.web.bind.annotation.*;

import java.util.ArrayList;

@RestController
@RequiredArgsConstructor
@RequestMapping("/recipe")
public class RecipeController {
    private final RecipeService recipeService;
    private final RecipeMapper recipeMapper;
    private final Logger logger = LoggerFactory.getLogger(RecipeController.class);

    @PostMapping(consumes = "application/json")
    public ResponseEntity<RecipeDTO> createRecipe(@Valid @RequestBody CreateRecipeDTO createRecipeDTO, final JwtAuthenticationToken jwt) {
        var subject = (String) jwt.getTokenAttributes().get("sub");

        var recipe = recipeMapper.createRecipeToRecipe(createRecipeDTO, subject);

        var savedRecipe = this.recipeService.saveRecipe(recipe);

        return ResponseEntity.ok(recipeMapper.recipeToRecipeDTO(savedRecipe));
    }

    @GetMapping("/{id}")
    public ResponseEntity<RecipeDTO> getRecipe(final JwtAuthenticationToken jwt, @PathVariable long id) {
        var subject = (String) jwt.getTokenAttributes().get("sub");

        var recipe = this.recipeService.getRecipe(id, subject);

        return ResponseEntity.ok(recipeMapper.recipeToRecipeDTO(recipe));
    }

    @PutMapping("/{id}")
    public ResponseEntity<RecipeDTO> updateRecipe(final JwtAuthenticationToken jwt, @PathVariable long id, @Valid @RequestBody CreateRecipeDTO createRecipeDTO) {
        var subject = (String) jwt.getTokenAttributes().get("sub");

        var recipe = this.recipeService.updateRecipe(id, subject, createRecipeDTO);

        return ResponseEntity.ok(recipeMapper.recipeToRecipeDTO(recipe));
    }

    @PostMapping("/{id}/ingredient")
    public ResponseEntity<ArrayList<IngredientDTO>> addIngredientToRecipe(final JwtAuthenticationToken jwt, @PathVariable long id, @Valid @RequestBody CreateIngredientDTO createIngredientDTO) {
        var subject = (String) jwt.getTokenAttributes().get("sub");

        var ingredientsList = this.recipeService.addIngredientToRecipe(id, subject, createIngredientDTO);

        return ResponseEntity.ok(ingredientsList.getIngredients());
    }

    @GetMapping("/{id}/ingredients")
    public ResponseEntity<ArrayList<IngredientDTO>> getIngredients(final JwtAuthenticationToken jwt, @PathVariable long id) {
        var subject = (String) jwt.getTokenAttributes().get("sub");

        var ingredientList = this.recipeService.getIngredientsFromRecipe(id, subject);

        return ResponseEntity.ok(ingredientList);
    }
}
