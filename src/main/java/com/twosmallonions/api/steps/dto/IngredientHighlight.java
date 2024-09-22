package com.twosmallonions.api.steps.dto;

import lombok.Data;

import java.util.UUID;

@Data
public class IngredientHighlight {
    private UUID ingredientId;
    private int highlightStart;
    private int highlightEnd;
}
