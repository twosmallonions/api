package com.twosmallonions.api.ingredients.dto;

import jakarta.validation.constraints.NotBlank;
import lombok.Data;

import java.util.UUID;

@Data
public class CreateIngredientDTO {
    @NotBlank
    String title;
    Boolean heading = false;

    String parsed_ingredient;

    double parsed_original_amount;
    String parsed_original_unit;
    String original_measurement_system;

}
