package com.twosmallonions.api.steps.dto;

import lombok.Data;

import java.util.UUID;

@Data
public class StepsDTO {
    UUID id;
    String description;
    Boolean heading;

    UUID[] ingredients;
    String[] images;
    StepTimer[] timers;
    IngredientHighlight[] highlights;
}
