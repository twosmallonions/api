package com.twosmallonions.api.tags.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Pattern;
import lombok.Data;
import org.hibernate.validator.constraints.Length;

@Data
public class CreateTagDTO {
    @NotBlank
    private String text;
    @Length(min = 7, max = 7)
    @Pattern(regexp = "^#[a-f0-9]{6}$")
    private String color = "#ff7f50";
}
