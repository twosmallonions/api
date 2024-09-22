package com.twosmallonions.api.steps.dto;

import jakarta.validation.constraints.NotBlank;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;
import lombok.experimental.SuperBuilder;

import java.io.Serializable;
import java.util.ArrayList;
import java.util.UUID;

@Data
@NoArgsConstructor
public class CreateStepDTO implements Serializable {
    @NotBlank
    private String description;
    private Boolean heading;

}
