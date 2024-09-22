package com.twosmallonions.api.images;

import com.fasterxml.uuid.Generators;
import com.twosmallonions.api.recipe.RecipeRepository;
import com.twosmallonions.api.recipe.RecipeService;
import jakarta.validation.constraints.NotNull;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.client.RestClient;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.io.InputStream;
import java.net.URI;
import java.time.ZonedDateTime;
import java.util.List;
import java.util.UUID;

@Service
public class ImageUploadService {
    private final ImageUploader uploader;
    private final RestClient restClient;
    private final RecipeService recipeService;
    private final RecipeRepository recipeRepository;
    @Value("${tso.upload.user-image-bucket:}")
    private String userImageBucket;
    @Value("${tso.upload.imgproxy-base-url:}")
    private String imageProxyBaseUrl;

    public ImageUploadService(
            RestClient.Builder restClientBuilder,
            RecipeService recipeService,
            ImageUploader uploader,
            RecipeRepository recipeRepository
    ) {
        this.recipeService = recipeService;
        this.restClient = restClientBuilder.build();
        this.uploader = uploader;
        this.recipeRepository = recipeRepository;
    }


    private void uploadAndProcessImage(InputStream inputStream, long size, ImageFile imageFile) throws IOException {
        this.uploader.uploadObject(inputStream, size, imageFile.getTemporaryPath(), this.userImageBucket);
        for (var format: imageFile.getFormats()) {
            convertAndMakeThumbnailRecipeCoverImage(imageFile, format);
        }
    }

    private void convertAndMakeThumbnailRecipeCoverImage(ImageFile imageFile, String extension) throws IOException {
        String objectOutputPath = imageFile.getFullPath(extension);
        String thumbnailOutputPath = imageFile.getFullThumbnailPath(extension);

        String imagePath = ImgproxyUriBuilder
                .fromUrl(this.imageProxyBaseUrl)
                .withFilter("strip_metadata:1")
                .withFilter("quality:60")
                .withSourcePath("s3://" + userImageBucket + "/" + imageFile.getTemporaryPath())
                .withExtension(extension)
                .build();
        // Generate original image conversion path

        // Convert and upload original image
        uploadImage(imagePath, objectOutputPath);
        String thumbnailPath = ImgproxyUriBuilder
                .fromUrl(this.imageProxyBaseUrl)
                .withFilter("resizing_type:fill-down")
                .withFilter("width:400")
                .withFilter("height:400")
                .withFilter("gravity:ce")
                .withSourcePath("s3://" + userImageBucket + "/" + objectOutputPath)
                .build();

        // Convert and upload thumbnail image
        uploadImage(thumbnailPath, thumbnailOutputPath);
    }

    private void uploadImage(String imagePath, String outputPath) throws IOException {
        var response = doRequest(imagePath);
        this.uploader.uploadObject(response, outputPath, this.userImageBucket);
    }

    private byte[] doRequest(String uri) throws IOException {
        return this.restClient.get()
                .uri(uri)
                .retrieve()
                .body(byte[].class);
    }

    @Transactional
    public void addImageToRecipe(UUID recipeId, String subject, MultipartFile file) throws IOException {
        this.checkContentType(file);
        var recipe = this.recipeService.getRecipe(recipeId, subject);
        var image = new RecipeImage();
        addImage(file, recipe, image, subject);

        this.recipeRepository.save(recipe);
    }

    public void addImage(MultipartFile file, ImageTarget target, ImageFile image, String subject) throws IOException {
        var imageId = Generators.timeBasedEpochGenerator().generate();
        var imageBase = subject + "/" + target.getId() + "/" + imageId;
        image.setUploaded(ZonedDateTime.now());
        image.setFullPath(imageBase + "/full");
        image.setFullThumbnailPath(imageBase + "/thumbnail");

        uploadAndProcessImage(file.getInputStream(), file.getSize(), image);

        target.addImage(image);
    }

    private void checkContentType(MultipartFile file) {
        if (file.getContentType() == null || !file.getContentType().split("/")[0].equals("image")) {
            throw new RuntimeException("Uploaded file is not an image");
        }
    }
}
