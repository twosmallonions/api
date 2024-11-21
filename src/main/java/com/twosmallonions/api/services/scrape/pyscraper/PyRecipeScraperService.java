package com.twosmallonions.api.services.scrape.pyscraper;

import com.twosmallonions.api.ScrapeRequest;
import com.twosmallonions.api.ScraperServiceGrpc;
import com.twosmallonions.api.recipe.Recipe;
import com.twosmallonions.api.services.scrape.RecipeScraper;
import io.grpc.Grpc;
import io.grpc.ManagedChannel;
import io.grpc.TlsChannelCredentials;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import java.io.File;
import java.io.IOException;
import java.net.URI;

@Service
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
    public Recipe parse(URI url) {
        var request = ScrapeRequest.newBuilder().setUrl(url.toString()).build();

        var response = this.blockingStub.scrape(request);
        logger.info(response.toString());

        return null;

    }
}
