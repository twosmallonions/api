package com.twosmallonions.api.exceptions;

import lombok.Data;
import lombok.EqualsAndHashCode;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.ResponseStatus;

@EqualsAndHashCode(callSuper = true)
@ResponseStatus(value = HttpStatus.NOT_FOUND, reason = "Resource was not found")
@Data
public class ResourceNotFoundException extends RuntimeException {
    private final String message;
    private final String code = "RESOURCE_NOT_FOUND";
    public ResourceNotFoundException(String message) {
        this.message = message;
    }
}
