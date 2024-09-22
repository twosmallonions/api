package com.twosmallonions.api.exceptions;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.ZonedDateTime;

@Data
@AllArgsConstructor
@NoArgsConstructor
@Builder
public class ErrorResponse {
    private String message;
    private String code;
    @Builder.Default
    private ZonedDateTime timestamp = ZonedDateTime.now();
    private int status;
    private String path;
}
