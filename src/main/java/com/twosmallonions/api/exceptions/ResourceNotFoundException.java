package com.twosmallonions.api.exceptions;

import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.ResponseStatus;

@ResponseStatus(value = HttpStatus.NOT_FOUND, reason = "Resource was not found")
public class ResourceNotFoundException extends RuntimeException {
}
