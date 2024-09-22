package com.twosmallonions.api.ingredients.dto;

import lombok.Data;

import java.io.Serializable;
import java.util.UUID;

@Data
public class IngredientDTO implements Serializable {
    UUID id;
    String title;
    Boolean heading;

    String parsed_ingredient;

    double parsed_original_amount;
    String parsed_original_unit;
    String original_measurement_system;

    double parsed_converted_amount;
    String parsed_converted_unit;
    String converted_measurement_system;
}
