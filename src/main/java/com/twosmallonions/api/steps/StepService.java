package com.twosmallonions.api.steps;

import com.fasterxml.uuid.Generators;
import com.twosmallonions.api.exceptions.ResourceNotFoundException;
import com.twosmallonions.api.recipe.Recipe;
import com.twosmallonions.api.recipe.RecipeService;
import com.twosmallonions.api.steps.dto.CreateStepDTO;
import com.twosmallonions.api.steps.dto.StepDTO;
import com.twosmallonions.api.steps.ingredient.StepIngredientDTO;
import com.twosmallonions.api.steps.ingredient.StepIngredientRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.UUID;

@Service
@RequiredArgsConstructor
public class StepService {
    private final StepRepository stepRepository;
    private final RecipeService recipeService;
    private final StepMapper stepMapper;
    private final StepIngredientRepository stepIngredientRepository;

    @Transactional
    public List<StepDTO> addStepToRecipe(UUID id, String subject, CreateStepDTO createStepDTO) {
        var recipe = this.recipeService.getRecipe(id, subject);

        var step = this.stepMapper.createStepDTOToStep(createStepDTO, recipe.getSteps().size());

        recipe.addStep(step);
        this.stepRepository.save(step);

        return recipe.getSteps().stream().map(this.stepMapper::stepToStepDTO).toList();
    }

    public List<StepDTO> getStepsFromRecipe(UUID id, String subject) {
        var recipe = this.recipeService.getRecipe(id, subject);
        return recipe.getSteps().stream().map(this.stepMapper::stepToStepDTO).toList();
    }

    @Transactional
    public StepDTO addIngredientToStep(UUID recipeId, UUID stepID, String subject, StepIngredientDTO stepIngredientDTO) {
        var recipe = this.recipeService.getRecipe(recipeId, subject);
        var step = recipe.getSteps().stream().filter(stepIter -> stepIter.getId().equals(stepID)).findFirst();

        if (step.isEmpty()) {
            throw new ResourceNotFoundException("step on id " + stepID + " not found");
        }

        var ingredient = recipe.getIngredient().stream().filter(ingredientIter -> ingredientIter.getId().equals(UUID.fromString(stepIngredientDTO.getIngredientId()))).findFirst();

        if (ingredient.isEmpty()) {
            throw new ResourceNotFoundException("ingredient on id " + stepIngredientDTO.getIngredientId() + " not found");
        }


        var stepIngredient = this.stepMapper.stepIngredientDTOToStepIngredient(stepIngredientDTO);
        ingredient.get().addStepIngredient(stepIngredient);
        step.get().addStepIngredient(stepIngredient);
        this.stepIngredientRepository.save(stepIngredient);

        return this.stepMapper.stepToStepDTO(step.get());
    }

}
