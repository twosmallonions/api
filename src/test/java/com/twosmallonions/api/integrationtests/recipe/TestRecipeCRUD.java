package com.twosmallonions.api.integrationtests.recipe;

import com.jayway.jsonpath.JsonPath;
import com.twosmallonions.api.recipe.RecipeRepository;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.boot.testcontainers.service.connection.ServiceConnection;
import org.springframework.http.MediaType;
import org.springframework.security.oauth2.jwt.JwtDecoder;
import org.springframework.test.context.ActiveProfiles;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.web.context.WebApplicationContext;
import org.testcontainers.containers.PostgreSQLContainer;
import org.testcontainers.junit.jupiter.Container;
import org.testcontainers.junit.jupiter.Testcontainers;

import static org.springframework.security.test.web.servlet.request.SecurityMockMvcRequestPostProcessors.jwt;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;


@ActiveProfiles(profiles = "test")
@SpringBootTest
@AutoConfigureMockMvc()
@Testcontainers
class TestRecipeCRUD {

    @Container
    @ServiceConnection
    static PostgreSQLContainer<?> postgresContainer = new PostgreSQLContainer<>("postgres:16-bookworm");

    @Autowired private MockMvc mockMvc;
    @MockBean
    JwtDecoder jwtDecoder;
    @Test
    void testCreateRecipe() throws Exception {
        var testDescription = "This is a test description with some **fancy** __markdown__ which should be supported!";
        var recipeCreateRequest = String.format("""
{
    "title": "test",
    "description": "%s",
    "servings": "Serves 2",
    "originalUrl": "https://example.com",
    "prepTime": 30,
    "cookTime": 30,
    "restTime": 30,
    "note": "This is a random recipe note"
}""", testDescription);
        this.mockMvc.perform(
                post("/recipe")
                        .accept(MediaType.APPLICATION_JSON)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(recipeCreateRequest)
                        .with(jwt())
        ).andExpectAll(
                status().isOk(),
                content().contentType(MediaType.APPLICATION_JSON),
                jsonPath("$.title").value("test"),
                jsonPath("$.description").value(testDescription),
                jsonPath("$.servings").value("Serves 2"),
                jsonPath("$.originalUrl").value("https://example.com"),
                jsonPath("$.prepTime").value(30),
                jsonPath("$.cookTime").value(30),
                jsonPath("$.restTime").value(30),
                jsonPath("$.totalTime").value(90),
                jsonPath("$.note").value("This is a random recipe note")
        ).andReturn();
    }

    @Test
    void testGetRecipe() throws Exception {
        var testDescription = "This is a test description with some **fancy** __markdown__ which should be supported!";
        var recipeCreateRequest = String.format("""
{
    "title": "test",
    "description": "%s",
    "servings": "Serves 2",
    "originalUrl": "https://example.com",
    "prepTime": 30,
    "cookTime": 30,
    "restTime": 30,
    "note": "This is a random recipe note"
}""", testDescription);
        var res = this.mockMvc.perform(
                post("/recipe")
                        .accept(MediaType.APPLICATION_JSON)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(recipeCreateRequest)
                        .with(jwt())
        ).andExpectAll(
                status().isOk(),
                content().contentType(MediaType.APPLICATION_JSON),
                jsonPath("$.title").value("test"),
                jsonPath("$.description").value(testDescription),
                jsonPath("$.servings").value("Serves 2"),
                jsonPath("$.originalUrl").value("https://example.com"),
                jsonPath("$.prepTime").value(30),
                jsonPath("$.cookTime").value(30),
                jsonPath("$.restTime").value(30),
                jsonPath("$.totalTime").value(90),
                jsonPath("$.note").value("This is a random recipe note")
        ).andReturn();

        String id = JsonPath.read(res.getResponse().getContentAsString(), "$.id");

        this.mockMvc.perform(
                get("/recipe/" + id)
                        .accept(MediaType.APPLICATION_JSON)
                        .contentType(MediaType.APPLICATION_JSON)
                        .with(jwt())
        ).andExpectAll(
                status().isOk(),
                content().contentType(MediaType.APPLICATION_JSON),
                jsonPath("$.title").value("test"),
                jsonPath("$.description").value(testDescription),
                jsonPath("$.servings").value("Serves 2"),
                jsonPath("$.originalUrl").value("https://example.com"),
                jsonPath("$.prepTime").value(30),
                jsonPath("$.cookTime").value(30),
                jsonPath("$.restTime").value(30),
                jsonPath("$.totalTime").value(90),
                jsonPath("$.note").value("This is a random recipe note")
        ).andReturn();
    }

    @Test
    void testUpdateRecipe() throws Exception {
        // Create recipe
        var recipeCreateRequest = """
{
    "title": "test"
}""";
        var res = this.mockMvc.perform(
                post("/recipe")
                        .accept(MediaType.APPLICATION_JSON)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(recipeCreateRequest)
                        .with(jwt())
        ).andExpectAll(
                status().isOk(),
                content().contentType(MediaType.APPLICATION_JSON),
                jsonPath("$.title").value("test")
        ).andReturn();

        String id = JsonPath.read(res.getResponse().getContentAsString(), "$.id");

        // Add ingredient that we'll reference later
        var ingredient = """
{
    "notes": "Existing ingredient"
}""";

        var res2 = this.mockMvc.perform(
                post("/recipe/" + id + "/ingredient")
                        .accept(MediaType.APPLICATION_JSON)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(ingredient)
                        .with(jwt())
        ).andExpectAll(
                status().isOk(),
                content().contentType(MediaType.APPLICATION_JSON),
                jsonPath("$[0].notes").value("Existing ingredient")
        ).andReturn();

        String existingIngredientId = JsonPath.read(res2.getResponse().getContentAsString(), "$[0].id");

        // Add step
        var step = """
{
    "description": "First step"
}""";

        var res3 = this.mockMvc.perform(
                post("/recipe/" + id + "/step")
                        .accept(MediaType.APPLICATION_JSON)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(step)
                        .with(jwt())
        ).andExpectAll(
                status().isOk(),
                content().contentType(MediaType.APPLICATION_JSON),
                jsonPath("$[0].description").value("First step")
        ).andReturn();

        String existingStepId = JsonPath.read(res3.getResponse().getContentAsString(), "$[0].id");

        // Update recipe with linked ingredients in steps
        var recipeUpdate = String.format("""
{
    "title": "UPDATED_TITLE",
    "ingredients": [
        {"id": "%s", "notes": "Updated existing ingredient"},
        {"id": "temp1", "notes": "New ingredient 1"},
        {"id": "temp2", "notes": "New ingredient 2"}
    ],
    "steps": [
        {
            "id": "%s",
            "description": "Mix ingredients",
            "linkedIngredients": [
                {
                    "ingredientId": "%s",
                    "highlight": true,
                    "highlightStart": 0,
                    "highlightEnd": 3
                },
                {
                    "ingredientId": "temp1",
                    "highlight": true,
                    "highlightStart": 4,
                    "highlightEnd": 7
                }
            ]
        },
        {
            "id": "temp1",
            "description": "Add remaining ingredient",
            "linkedIngredients": [
                {
                    "ingredientId": "temp2",
                    "highlight": false,
                    "highlightStart": 0,
                    "highlightEnd": 0
                }
            ]
        }
    ]
}""", existingIngredientId, existingStepId, existingIngredientId);

        // Perform update and store response for ID extraction
        var updateResult = this.mockMvc.perform(
                put("/recipe/" + id)
                        .accept(MediaType.APPLICATION_JSON)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(recipeUpdate)
                        .with(jwt())
        ).andExpectAll(
                status().isOk(),
                content().contentType(MediaType.APPLICATION_JSON),
                // Verify basic recipe update
                jsonPath("$.title").value("UPDATED_TITLE"),

                // Verify ingredients
                jsonPath("$.ingredients[0].id").value(existingIngredientId),
                jsonPath("$.ingredients[0].notes").value("Updated existing ingredient"),
                jsonPath("$.ingredients[1].notes").value("New ingredient 1"),
                jsonPath("$.ingredients[2].notes").value("New ingredient 2"),

                // Verify first step with linked ingredients
                jsonPath("$.steps[0].id").value(existingStepId),
                jsonPath("$.steps[0].description").value("Mix ingredients"),
                jsonPath("$.steps[0].linkedIngredients[0].ingredientId").value(existingIngredientId),
                jsonPath("$.steps[0].linkedIngredients[0].highlight").value(true),
                jsonPath("$.steps[0].linkedIngredients[0].highlightStart").value(0),
                jsonPath("$.steps[0].linkedIngredients[0].highlightEnd").value(3)
        ).andReturn();

        // Extract new ingredient IDs from response
        String responseJson = updateResult.getResponse().getContentAsString();
        String newIngredientId1 = JsonPath.read(responseJson, "$.ingredients[1].id");
        String newIngredientId2 = JsonPath.read(responseJson, "$.ingredients[2].id");

        // Additional verification with extracted IDs
        this.mockMvc.perform(
                get("/recipe/" + id + "/full")
                        .accept(MediaType.APPLICATION_JSON)
                        .with(jwt())
        ).andExpectAll(
                status().isOk(),
                content().contentType(MediaType.APPLICATION_JSON),
                // Verify steps reference the correct ingredient IDs
                jsonPath("$.ingredients[0].id").value(existingIngredientId),
                jsonPath("$.ingredients[0].notes").value("Updated existing ingredient"),
                jsonPath("$.ingredients[1].id").value(newIngredientId1),
                jsonPath("$.ingredients[1].notes").value("New ingredient 1"),
                jsonPath("$.ingredients[2].id").value(newIngredientId2),
                jsonPath("$.ingredients[2].notes").value("New ingredient 2"),

                // Verify first step completely
                jsonPath("$.steps[0].id").value(existingStepId),
                jsonPath("$.steps[0].description").value("Mix ingredients"),
                // First linked ingredient in first step
                jsonPath("$.steps[0].linkedIngredients[1].ingredientId").value(existingIngredientId),
                jsonPath("$.steps[0].linkedIngredients[1].highlight").value(true),
                jsonPath("$.steps[0].linkedIngredients[1].highlightStart").value(0),
                jsonPath("$.steps[0].linkedIngredients[1].highlightEnd").value(3),
                // Second linked ingredient in first step
                jsonPath("$.steps[0].linkedIngredients[0].ingredientId").value(newIngredientId1),
                jsonPath("$.steps[0].linkedIngredients[0].highlight").value(true),
                jsonPath("$.steps[0].linkedIngredients[0].highlightStart").value(4),
                jsonPath("$.steps[0].linkedIngredients[0].highlightEnd").value(7),

                // Verify second step completely
                jsonPath("$.steps[1].description").value("Add remaining ingredient"),
                jsonPath("$.steps[1].linkedIngredients[0].ingredientId").value(newIngredientId2),
                jsonPath("$.steps[1].linkedIngredients[0].highlight").value(false),
                jsonPath("$.steps[1].linkedIngredients[0].highlightStart").value(0),
                jsonPath("$.steps[1].linkedIngredients[0].highlightEnd").value(0)
        );
    }
}
