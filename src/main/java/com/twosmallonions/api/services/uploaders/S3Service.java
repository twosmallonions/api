package com.twosmallonions.api.services.uploaders;

import com.twosmallonions.api.images.ImageUploader;
import lombok.SneakyThrows;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;
import org.springframework.stereotype.Service;
import software.amazon.awssdk.auth.credentials.AwsBasicCredentials;
import software.amazon.awssdk.auth.credentials.StaticCredentialsProvider;
import software.amazon.awssdk.core.sync.RequestBody;
import software.amazon.awssdk.http.apache.ApacheHttpClient;
import software.amazon.awssdk.regions.Region;
import software.amazon.awssdk.services.s3.S3Client;
import software.amazon.awssdk.services.s3.model.GetObjectRequest;
import software.amazon.awssdk.services.s3.model.PutObjectRequest;
import software.amazon.awssdk.services.s3.presigner.S3Presigner;
import software.amazon.awssdk.services.s3.presigner.model.GetObjectPresignRequest;

import java.io.InputStream;
import java.net.URI;
import java.net.URL;
import java.time.Duration;

@Component
public class S3Service implements ImageUploader {
    private final S3Client s3Client;
    private final S3Presigner s3Presigner;
    public S3Service(
            @Value("${tso.upload.endpoint:}") String endpoint,
            @Value("${tso.upload.aws-access-key:}") String awsAccessKey,
            @Value("${tso.upload.aws-secret-key:}") String awsSecretKey,
            @Value("${tso.upload.region:}") String region
    ) {
        this.s3Client = S3Client
                .builder()
                .credentialsProvider(StaticCredentialsProvider.create(AwsBasicCredentials.create(awsAccessKey, awsSecretKey)))
                .region(Region.of(region))
                .endpointOverride(URI.create(endpoint))
                .httpClientBuilder(ApacheHttpClient.builder()
                        .maxConnections(100)
                        .connectionTimeout(Duration.ofSeconds(5))
                ).build();
        this.s3Presigner = S3Presigner.builder()
                .credentialsProvider(StaticCredentialsProvider.create(AwsBasicCredentials.create(awsAccessKey, awsSecretKey)))
                .region(Region.of(region))
                .endpointOverride(URI.create(endpoint))
                .build();

    }

    @SneakyThrows // FIXME: remove this and properly deal with exceptions
    public void uploadObject(InputStream inputStream, long size, String object, String bucket) {
        var putObjectRequest = this.createPutObjectRequest(object, bucket);
        var requestBody = RequestBody.fromInputStream(inputStream, size);
        this.s3Client.putObject(putObjectRequest, requestBody);
    }


    @SneakyThrows // FIXME: remove this and properly deal with exceptions
    public void uploadObject(byte[] body, String object, String bucket) {
        var putObjectRequest = this.createPutObjectRequest(object, bucket);
        var requestBody = RequestBody.fromBytes(body);
        this.s3Client.putObject(putObjectRequest, requestBody);
    }

    private PutObjectRequest createPutObjectRequest(String object, String bucket) {
        return PutObjectRequest.builder()
                .bucket(bucket)
                .key(object)
                .contentType(this.determineContentType(object))
                .build();
    }

    public URL getObjectUri(String bucket, String path) {
        var getObjectRequest = GetObjectRequest.builder()
                .bucket(bucket)
                .key(path)
                .build();

        var getObjectPresignRequest = GetObjectPresignRequest.builder()
                .getObjectRequest(getObjectRequest)
                .signatureDuration(Duration.ofHours(1))
                .build();

        var req =  this.s3Presigner.presignGetObject(getObjectPresignRequest);
        return req.url();
    }

    private String determineContentType(String fileName) {
        String extension = fileName.substring(fileName.lastIndexOf(".") + 1).toLowerCase();
        return switch (extension) {
            case "jpg", "jpeg" -> "image/jpeg";
            case "png" -> "image/png";
            case "gif" -> "image/gif";
            case "svg" -> "image/svg+xml";
            case "webp" -> "image/webp";
            case "tiff", "tif" -> "image/tiff";
            case "bmp" -> "image/bmp";
            case "ico" -> "image/x-icon";
            case "heic" -> "image/heic";
            case "heif" -> "image/heif";
            case "avif" -> "image/avif";
            default -> "application/octet-stream";
        };
    }
}
