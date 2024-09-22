package com.twosmallonions.api.images;

import org.springframework.web.util.UriComponentsBuilder;

import java.util.ArrayList;
import java.util.Base64;

public class ImgproxyUriBuilder {
    private final UriComponentsBuilder uriBuilder;
    private final ArrayList<String> filters;
    private String extension;
    private String sourcePath;

    private ImgproxyUriBuilder(String url) {
        this.uriBuilder = UriComponentsBuilder.fromHttpUrl(url);
        this.filters = new ArrayList<>();
    }

    public static ImgproxyUriBuilder fromUrl(String url) {
        return new ImgproxyUriBuilder(url);
    }

    public ImgproxyUriBuilder withFilter(String filter) {
        this.filters.add(filter);
        return this;
    }

    public ImgproxyUriBuilder withSourcePath(String sourcePath) {
        this.sourcePath = sourcePath;
        return this;
    }

    public ImgproxyUriBuilder withExtension(String extension) {
        this.extension = extension;
        return this;
    }

    public String build() {
        uriBuilder
                .path("insecure");

        for (String filter : filters) {
            uriBuilder.pathSegment(filter);
        }
        var sourcePathBase64 = Base64.getUrlEncoder().withoutPadding().encodeToString(this.sourcePath.getBytes());
        if (this.extension != null) {
            sourcePathBase64 += "." + this.extension;
        }
        uriBuilder.pathSegment(sourcePathBase64);

        return uriBuilder.toUriString();
    }

}
