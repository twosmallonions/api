package com.twosmallonions.api.images;

import com.twosmallonions.api.services.uploaders.S3Service;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import java.net.URL;
import java.util.ArrayList;
import java.util.List;

@Service
public class ImageMapper {
    private final String bucket;
    private final S3Service s3Service;
    public ImageMapper(
            @Value("${tso.upload.user-image-bucket:}") String bucket,
            S3Service s3Service
    ) {
        this.bucket = bucket;
        this.s3Service = s3Service;
    }

    public URL asURL(String path) {
        return this.s3Service.getObjectUri(this.bucket, path);
    }

    public List<URL> recipeImageAsURL(RecipeImage recipeImage) {
        if (recipeImage == null) {
            return new ArrayList<>();
        }
        return recipeImage.getFormats()
                .stream()
                .map(format -> this.asURL(recipeImage.getFullPath(format)))
                .toList();
    }
}
