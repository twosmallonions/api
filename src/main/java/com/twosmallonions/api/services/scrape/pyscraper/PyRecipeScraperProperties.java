package com.twosmallonions.api.services.scrape.pyscraper;

import lombok.Getter;
import lombok.Setter;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.context.annotation.Configuration;

import java.net.URI;

@Getter
@Setter
@Configuration
@ConfigurationProperties(prefix = "tso.scraper.py")
public class PyRecipeScraperProperties {
    private String host;
    private int port;
    private String clientCertificate;
    private String clientKey;
    private String rootCa;
    private boolean enabled;
}
