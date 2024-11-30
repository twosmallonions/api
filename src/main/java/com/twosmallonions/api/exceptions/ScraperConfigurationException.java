package com.twosmallonions.api.exceptions;

import lombok.EqualsAndHashCode;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.ResponseStatus;

@EqualsAndHashCode(callSuper=true)
@ResponseStatus(value = HttpStatus.BAD_REQUEST, reason = "No scraper configured")
public class ScraperConfigurationException extends RuntimeException{
    private String message;
    private final String code = "SCRAPER_CONFIGURATION";

    public ScraperConfigurationException(String message) {
        this.message = message;
    }
}
