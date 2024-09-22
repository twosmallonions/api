package com.twosmallonions.api.steps.ingredient;

import jakarta.validation.constraints.NotNull;
import lombok.Data;

import java.io.Serializable;
import java.util.UUID;

@Data
public class StepIngredientDTO implements Serializable {
    private boolean highlight;
    private int highlightStart;
    private int highlightEnd;
    @NotNull
    private String ingredientId;
}
