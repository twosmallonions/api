package com.twosmallonions.api.images;

import lombok.Getter;
import lombok.Setter;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.context.annotation.Configuration;

@Getter
@Setter
@Configuration
@ConfigurationProperties(prefix = "tso.upload")
public class ImageUploadConfigProperties {
    private String endpoint;
    private String awsSecretKey;
    private String awsAccessKey;
    private String userImageBucket;
    private String imgproxyBaseUrl;
    private String region;
}
