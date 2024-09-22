package com.twosmallonions.api.recipe;

import com.twosmallonions.api.ingredients.IngredientService;
import com.twosmallonions.api.ingredients.IngredientsMapper;
import com.twosmallonions.api.ingredients.dto.IngredientDTO;
import com.twosmallonions.api.ingredients.dto.CreateIngredientDTO;
import com.twosmallonions.api.recipe.dto.CreateRecipeDTO;
import com.twosmallonions.api.recipe.dto.FullRecipeDTO;
import com.twosmallonions.api.recipe.dto.RecipeDTO;
import com.twosmallonions.api.recipe.dto.UpdateRecipeDTO;
import com.twosmallonions.api.steps.StepService;
import com.twosmallonions.api.steps.dto.CreateStepDTO;
import com.twosmallonions.api.steps.dto.StepDTO;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.oauth2.server.resource.authentication.JwtAuthenticationToken;
import org.springframework.web.bind.annotation.*;

import java.util.ArrayList;
import java.util.List;
import java.util.UUID;

@RestController
@RequiredArgsConstructor
@RequestMapping("/recipe")
public class RecipeController {
    private final RecipeService recipeService;
    private final RecipeMapper recipeMapper;
    private final IngredientService ingredientService;
    private final IngredientsMapper ingredientsMapper;
    private final StepService stepService;

    @GetMapping
    public ResponseEntity<List<RecipeDTO>> getAllRecipes(final JwtAuthenticationToken jwt) {
        var subject = (String) jwt.getTokenAttributes().get("sub");

        return ResponseEntity.ok(recipeService.getAllRecipes(subject));
    }

    @PutMapping("/{id}/like")
    public ResponseEntity<RecipeDTO> toggleRecipeLike(final JwtAuthenticationToken jwt, @PathVariable UUID id) {
        var subject = (String) jwt.getTokenAttributes().get("sub");
        return ResponseEntity.ok(this.recipeService.toggleLike(id, subject));
    }

    @GetMapping("/slug/{slug}")
    public ResponseEntity<FullRecipeDTO> getFullRecipeBySlug(final JwtAuthenticationToken jwt, @PathVariable final String slug) {
        var subject = (String) jwt.getTokenAttributes().get("sub");

        return ResponseEntity.ok(this.recipeService.getFullRecipeBySlug(slug, subject));
    }

    @PostMapping(consumes = "application/json")
    public ResponseEntity<RecipeDTO> createRecipe(@Valid @RequestBody CreateRecipeDTO createRecipeDTO, final JwtAuthenticationToken jwt) {
        var subject = (String) jwt.getTokenAttributes().get("sub");

        var recipe = recipeMapper.createRecipeToRecipe(createRecipeDTO, subject);

        var savedRecipe = this.recipeService.createRecipe(recipe);

        return ResponseEntity.ok(recipeMapper.recipeToRecipeDTO(savedRecipe));
    }

    @GetMapping("/{id}/full")
    public ResponseEntity<FullRecipeDTO> fullRecipe(final JwtAuthenticationToken jwt, @PathVariable UUID id) {
        var subject = (String) jwt.getTokenAttributes().get("sub");

        var recipe = this.recipeService.getFullRecipe(id, subject);

        return ResponseEntity.ok(recipe);
    }

    @GetMapping("/{id}")
    public ResponseEntity<RecipeDTO> getRecipe(final JwtAuthenticationToken jwt, @PathVariable UUID id) {
        var subject = (String) jwt.getTokenAttributes().get("sub");

        var recipe = this.recipeService.getRecipe(id, subject);

        return ResponseEntity.ok(recipeMapper.recipeToRecipeDTO(recipe));
    }

    @PutMapping("/{id}")
    public ResponseEntity<FullRecipeDTO> updateRecipe(final JwtAuthenticationToken jwt, @PathVariable UUID id, @Valid @RequestBody UpdateRecipeDTO updateRecipeDTO) {
        var subject = (String) jwt.getTokenAttributes().get("sub");

        var recipe = this.recipeService.updateRecipe(id, subject, updateRecipeDTO);

        return ResponseEntity.ok(recipe);
    }

    @PostMapping("/{id}/ingredient")
    public ResponseEntity<List<IngredientDTO>> addIngredientToRecipe(final JwtAuthenticationToken jwt, @PathVariable UUID id, @Valid @RequestBody CreateIngredientDTO createIngredientDTO) {
        var subject = (String) jwt.getTokenAttributes().get("sub");

        var ingredients = this.ingredientService.addIngredientToRecipe(id, subject, createIngredientDTO);

        var ingredientDTOs = ingredients.stream().map(ingredientsMapper::ingredientToIngredientDTO).toList();
        return ResponseEntity.ok(ingredientDTOs);
    }

    @GetMapping("/{id}/ingredients")
    public ResponseEntity<List<IngredientDTO>> getIngredients(final JwtAuthenticationToken jwt, @PathVariable UUID id) {
        var subject = (String) jwt.getTokenAttributes().get("sub");

        var ingredients = this.ingredientService.getIngredientsFromRecipe(id, subject);

        var ingredientDTOs = ingredients.stream().map(ingredientsMapper::ingredientToIngredientDTO).toList();
        return ResponseEntity.ok(ingredientDTOs);
    }

    @PutMapping("/{id}/ingredients")
    public ResponseEntity<List<IngredientDTO>> updateRecipeIngredients(final JwtAuthenticationToken jwt, @PathVariable UUID id, @Valid @RequestBody ArrayList<IngredientDTO> ingredientDTO) {
        return null;
    }

    @PostMapping("/{id}/step")
    public ResponseEntity<List<StepDTO>> addStepToRecipe(final JwtAuthenticationToken jwt, @PathVariable UUID id, @Valid @RequestBody CreateStepDTO createStepDTO) {
        var subject = (String) jwt.getTokenAttributes().get("sub");

        var steps = this.stepService.addStepToRecipe(id, subject, createStepDTO);

        return ResponseEntity.ok(steps);
    }

    @GetMapping("/{id}/steps")
    public ResponseEntity<List<StepDTO>> getSteps(final JwtAuthenticationToken jwt, @PathVariable UUID id) {
        var subject = (String) jwt.getTokenAttributes().get("sub");

        var steps = this.stepService.getStepsFromRecipe(id, subject);

        return ResponseEntity.ok(steps);
    }

    @PostMapping("/{id}/tag/{tagId}")
    @ResponseStatus(HttpStatus.NO_CONTENT)
    public void addTagToRecipe(final JwtAuthenticationToken jwt, @PathVariable UUID id, @PathVariable UUID tagId) {
        var subject = (String) jwt.getTokenAttributes().get("sub");

        //this.recipeService.addTagToRecipe(id, tagId, subject);

    }
}
