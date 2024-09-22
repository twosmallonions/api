package com.twosmallonions.api;

import com.twosmallonions.api.exceptions.ErrorResponse;
import com.twosmallonions.api.exceptions.ResourceNotFoundException;
import jakarta.servlet.http.HttpServletRequest;
import org.springframework.http.HttpStatus;
import org.springframework.http.HttpStatusCode;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.ControllerAdvice;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.ResponseBody;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.context.request.WebRequest;
import org.springframework.web.server.ResponseStatusException;
import org.springframework.web.servlet.mvc.method.annotation.ResponseEntityExceptionHandler;

@ControllerAdvice(basePackages = "com.twosmallonions.api")
public class ApiExceptionHandler extends ResponseEntityExceptionHandler {
    @ResponseBody
    @ExceptionHandler(value = {ResourceNotFoundException.class})
    protected ResponseEntity<ErrorResponse> handleException(HttpServletRequest httpRequest, ResourceNotFoundException ex) {
        var resp = ErrorResponse.builder()
                .status(HttpStatus.NOT_FOUND.value())
                .message(ex.getMessage())
                .code(ex.getCode())
                .path(httpRequest.getRequestURI())
                .build();

        return new ResponseEntity<>(resp, HttpStatusCode.valueOf(HttpStatus.NOT_FOUND.value()));
    }
}
