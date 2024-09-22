package com.twosmallonions.api.images;

import com.twosmallonions.api.recipe.RecipeService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.security.oauth2.server.resource.authentication.JwtAuthenticationToken;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.util.UUID;

@RequiredArgsConstructor
@Controller
@RequestMapping("/upload")
public class ImageUploadController {
    private final ImageUploadService imageUploadService;
    private final RecipeService recipeService;

    @PostMapping("/recipe/{id}")
    @ResponseStatus(HttpStatus.NO_CONTENT)
    public void addImageToRecipe(@RequestParam("file") MultipartFile file, @PathVariable UUID id, JwtAuthenticationToken jwt) throws IOException {
        var subject = (String) jwt.getTokenAttributes().get("sub");
        this.imageUploadService.addImageToRecipe(id, subject, file);
    }
}
