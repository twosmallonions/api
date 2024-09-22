package com.twosmallonions.api.services.scrape.pyscraper;

import com.twosmallonions.api.recipe.Recipe;
import com.twosmallonions.api.services.scrape.RecipeScraper;
import com.twosmallonions.api.services.scrape.pyscraper.response.RecipeScraperResponse;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpStatusCode;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestClient;
import org.springframework.web.util.UriComponentsBuilder;

import java.net.URI;

@Service
public class PyRecipeScraperService implements RecipeScraper {
    private final RestClient restClient;
    @Value("${tso.scraper.py.uri}")
    private URI scraperBaseUri;
    @Value("${tso.scraper.py.secret}")
    private String scraperSecret;

    public PyRecipeScraperService(RestClient.Builder clientBuilder) {
        this.restClient = clientBuilder.build();
    }

    @Override
    public String getHtml(URI uri) {
        var req = this.createRequest(uri, true);
        return req
                .retrieve()
                .body(String.class);
    }

    @Override
    public Recipe parse(URI uri) {
        var req = this.createRequest(uri, false);
        return req
                .retrieve()
                .body(RecipeScraperResponse.class)
                .toRecipe();
    }

    private RestClient.RequestHeadersSpec<?> createRequest(URI uri, boolean raw) {
        var scraperRequestUri = UriComponentsBuilder.fromUri(this.scraperBaseUri)
                .pathSegment("scrape")
                .queryParam("url", uri)
                .queryParam("raw", raw)
                .toUriString();

        var req = this.restClient
                .get()
                .uri(scraperRequestUri)
                .header("Authorization", "Bearer " + this.scraperSecret);

        if (raw)
            req.accept(MediaType.TEXT_PLAIN);
        else
            req.accept(MediaType.APPLICATION_JSON);

        return req;
    }
}
