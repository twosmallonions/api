package com.twosmallonions.api.recipeimport;

import com.twosmallonions.api.recipe.RecipeMapper;
import com.twosmallonions.api.recipe.dto.RecipeDTO;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.security.oauth2.server.resource.authentication.JwtAuthenticationToken;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.net.URI;
import java.net.URL;

@RestController
@RequiredArgsConstructor
@RequestMapping("/import")
public class RecipeImportController {
    private final RecipeImportService importService;
    private final RecipeMapper recipeMapper;
    @PostMapping("/url")
    public ResponseEntity<RecipeDTO> importRecipeFromUrl(@RequestParam URL url, JwtAuthenticationToken jwt) {
        var subject = (String) jwt.getTokenAttributes().get("sub");

        try {
            var recipe = this.importService.importRecipeFromUrl(url, subject);
            return ResponseEntity.ok(this.recipeMapper.recipeToRecipeDTO(recipe));
        } catch (Exception e) {
            throw new RuntimeException(e);
        }
    }
}
