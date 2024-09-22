package com.twosmallonions.api.ingredients.dto;

import jakarta.validation.constraints.NotBlank;
import lombok.Builder;
import lombok.Data;

@Data
public class CreateIngredientDTO {
    @NotBlank
    private String notes;
    private Boolean heading = false;

    private String parsedIngredient;

    private double parsedOriginalAmount;
    private String parsedOriginalUnit;
    private String originalMeasurementSystem;
}
