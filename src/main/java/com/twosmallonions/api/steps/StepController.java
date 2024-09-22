package com.twosmallonions.api.steps;

import com.twosmallonions.api.steps.dto.StepDTO;
import com.twosmallonions.api.steps.ingredient.StepIngredientDTO;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.security.oauth2.server.resource.authentication.JwtAuthenticationToken;
import org.springframework.web.bind.annotation.*;

import java.util.UUID;

@RestController
@RequiredArgsConstructor
public class StepController {
    private final StepService stepService;
    @PostMapping("/recipe/{recipe_id}/step/{step_id}/ingredient")
    public ResponseEntity<StepDTO> addIngredientToStep(@PathVariable("recipe_id") UUID recipeId, @PathVariable("step_id") UUID stepId, JwtAuthenticationToken jwt, @Valid @RequestBody StepIngredientDTO stepIngredientDTO) {
        var subject = (String) jwt.getTokenAttributes().get("sub");
        var step = this.stepService.addIngredientToStep(recipeId, stepId, subject, stepIngredientDTO);

        return ResponseEntity.ok(step);
    }
}
