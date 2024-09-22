package com.twosmallonions.api.steps;

import com.fasterxml.uuid.Generators;
import com.twosmallonions.api.recipe.Recipe;
import com.twosmallonions.api.steps.dto.StepDTO;
import com.twosmallonions.api.steps.ingredient.StepIngredient;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.HashMap;
import java.util.List;
import java.util.UUID;

@Service
@RequiredArgsConstructor
public class UpdateStepsService {
    private final StepRepository stepRepository;
    private final StepMapper stepMapper;


    @Transactional
    public void updateRecipeSteps(Recipe recipe, List<StepDTO> newSteps, HashMap<String, String> ingredientIdMap) {
        recipe.removeAllSteps();
        for (int orderIdx = 0; orderIdx < newSteps.size(); orderIdx++) {
            var stepDTO = newSteps.get(orderIdx);
            var step = this.updateOrCreateStep(stepDTO, recipe, ingredientIdMap);

            step.setOrder_idx(orderIdx);
            recipe.addStep(step);
        }
    }

    @Transactional
    protected Step updateOrCreateStep(StepDTO stepDTO, Recipe recipe, HashMap<String, String> ingredientIdMap) {
        Step step;
        try {
            var stepUUID = UUID.fromString(stepDTO.getId());

            var tmpStep = this.stepRepository.findById(stepUUID);

            if (tmpStep.isEmpty()) {
                step = this.stepMapper.stepDTOToStep(stepDTO, 0);
            } else {
                step = tmpStep.get();
                this.stepMapper.updateStep(step, stepDTO);
            }
        } catch (IllegalArgumentException e) {
            stepDTO.setId(Generators.timeBasedEpochGenerator().generate().toString());
            step = this.stepMapper.stepDTOToStep(stepDTO, 0);
        }

        this.updateStepIngredients(step, stepDTO, recipe, ingredientIdMap);

        return step;
    }

    @Transactional
    protected void updateStepIngredients(Step step, StepDTO stepDTO, Recipe recipe, HashMap<String, String> ingredientIdMap) {
        step.getStepIngredients().clear();

        for (var stepIngredient : stepDTO.getLinkedIngredients()) {
            if (!ingredientIdMap.containsKey(stepIngredient.getIngredientId())) {
                throw new RuntimeException("Ingredient " + stepIngredient.getIngredientId() + " not found");
            }

            var mappedId = UUID.fromString(ingredientIdMap.get(stepIngredient.getIngredientId()));
            var stepIngredientEntity = this.stepMapper.stepIngredientDTOToStepIngredient(stepIngredient);
            var ingredient = recipe.getIngredient().stream().filter(i -> i.getId().equals(mappedId)).findFirst();
            if (ingredient.isEmpty()) {
                throw new RuntimeException("Ingredient " + mappedId + " not found");
            }

            stepIngredientEntity.setIngredient(ingredient.get());

            step.addStepIngredient(stepIngredientEntity);
        }
    }
}
