package com.twosmallonions.api.tags.dto;

import lombok.Data;

import java.util.UUID;

@Data
public class TagDTO {
    private String text;
    private String color;
    private UUID uuid;
}
