package com.twosmallonions.api.ingredients.dto;

import com.fasterxml.jackson.annotation.JsonIgnore;
import jakarta.validation.constraints.NotBlank;
import lombok.Builder;
import lombok.Data;

import java.io.Serializable;
import java.util.UUID;

@Data
public class IngredientDTO implements Serializable {
    @NotBlank
    private String id;
    @NotBlank
    private String notes;
    private Boolean heading = false;

    private String parsedIngredient;

    private double parsedOriginalAmount;
    private String parsedOriginalUnit;
    private String originalMeasurementSystem;

    private double parsedConvertedAmount;
    private String parsedConvertedUnit;
    private String convertedMeasurementSystem;
    @JsonIgnore
    private int orderIdx;


}
