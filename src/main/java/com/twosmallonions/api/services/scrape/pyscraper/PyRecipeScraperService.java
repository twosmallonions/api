package com.twosmallonions.api.services.scrape.pyscraper;

import com.twosmallonions.api.ScrapeRequest;
import com.twosmallonions.api.ScraperServiceGrpc;
import com.twosmallonions.api.ingredients.dto.CreateIngredientDTO;
import com.twosmallonions.api.recipe.Recipe;
import com.twosmallonions.api.recipe.dto.CreateRecipeDTO;
import com.twosmallonions.api.services.scrape.RecipeScraper;
import com.twosmallonions.api.steps.dto.CreateStepDTO;
import io.grpc.Grpc;
import io.grpc.ManagedChannel;
import io.grpc.TlsChannelCredentials;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.stereotype.Service;

import java.io.File;
import java.io.IOException;
import java.net.URI;
import java.net.URL;
import java.util.ArrayList;

@Service
@ConditionalOnProperty(name = "tso.scraper.py.enabled", havingValue = "true")
public class PyRecipeScraperService implements RecipeScraper {

    private final ScraperServiceGrpc.ScraperServiceBlockingStub blockingStub;
    private static final Logger logger = LoggerFactory.getLogger(PyRecipeScraperService.class);

    PyRecipeScraperService(
            @Value("${tso.scraper.py.client-certificate}") String clientCertificate,
            @Value("${tso.scraper.py.client-key}") String clientKey,
            @Value("${tso.scraper.py.root-ca}") String rootCA,
            @Value("${tso.scraper.py.host}") String host,
            @Value("${tso.scraper.py.port}") int port
    ) throws IOException {
        var tls = TlsChannelCredentials
                .newBuilder()
                .keyManager(new File(clientCertificate), new File(clientKey))
                .trustManager(new File(rootCA))
                .build();
        var channel = Grpc.newChannelBuilderForAddress(host, port, tls).build();
        this.blockingStub = ScraperServiceGrpc.newBlockingStub(channel);
    }

    @Override
    public CreateRecipeDTO parse(URL url) {
        var request = ScrapeRequest.newBuilder().setUrl(url.toString()).build();

        var response = this.blockingStub.scrape(request);
        logger.info(response.toString());

        var createRecipe = new CreateRecipeDTO();
        createRecipe.setOriginalUrl(response.getCanonicalUrl());
        createRecipe.setCookTime(response.getCookTime());
        createRecipe.setDescription(response.getDescription());
        createRecipe.setIngredients(new ArrayList<>());
        for (var ingredient : response.getIngredientsList()) {
            var createIngredient = new CreateIngredientDTO();
            createIngredient.setNotes(ingredient);
            createRecipe.getIngredients().add(createIngredient);
        }

        createRecipe.setSteps(new ArrayList<>());
        for (var step: response.getInstructionsListList()) {
            var createStep = new CreateStepDTO();
            createStep.setDescription(step);
            createRecipe.getSteps().add(createStep);
        }

        createRecipe.setPrepTime(response.getPrepTime());
        createRecipe.setTitle(response.getTitle());

        return createRecipe;
    }
}
