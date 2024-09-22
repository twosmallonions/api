package com.twosmallonions.api.steps.dto;

import com.twosmallonions.api.steps.ingredient.StepIngredientDTO;
import lombok.Builder;
import lombok.Data;
import lombok.EqualsAndHashCode;
import lombok.NoArgsConstructor;
import lombok.experimental.SuperBuilder;

import java.io.Serializable;
import java.util.ArrayList;
import java.util.List;
import java.util.UUID;

@Data
public class StepDTO implements Serializable {
    private String id;
    private String description;
    private boolean heading;
    private List<StepIngredientDTO> linkedIngredients;
}
