package com.twosmallonions.api.steps;

import com.twosmallonions.api.steps.dto.CreateStepDTO;
import com.twosmallonions.api.steps.dto.StepDTO;
import com.twosmallonions.api.steps.ingredient.StepIngredient;
import com.twosmallonions.api.steps.ingredient.StepIngredientDTO;
import org.mapstruct.Mapper;
import org.mapstruct.Mapping;
import org.mapstruct.MappingTarget;
import org.mapstruct.factory.Mappers;

import java.util.Comparator;
import java.util.List;

@Mapper(componentModel = "spring")
public interface StepMapper {
    StepMapper INSTANCE = Mappers.getMapper(StepMapper.class);

    @Mapping(target = "id", ignore = true)
    Step createStepDTOToStep(CreateStepDTO createStepDTO, int order_idx);
    @Mapping(target = "ingredientId", source = "ingredient.id")
    StepIngredientDTO stepIngredientToStepIngredientDTO(StepIngredient stepIngredient);

    @Mapping(target = "ingredient", ignore = true)
    @Mapping(target = "step", ignore = true)
    StepIngredient stepIngredientDTOToStepIngredient(StepIngredientDTO stepIngredientDTO);

    @Mapping(target = "linkedIngredients", source = "stepIngredients")
    StepDTO stepToStepDTO(Step step);

    Step stepDTOToStep(StepDTO stepDTO, int orderIdx);


    void updateStep(@MappingTarget Step step, StepDTO stepDTO);

    default List<StepDTO> sortedStepMapper(List<Step> steps) {
        if (steps == null) {
            return null;
        }

        return steps.stream()
                .sorted(Comparator.comparingInt(Step::getOrder_idx))
                .map(this::stepToStepDTO)
                .toList();
    }
}
