package com.twosmallonions.api.steps.dto;

import lombok.Data;

@Data
public class StepTimer {
    private long duration;
    private int highlightStart;
    private int highlightEnd;
}
