package com.twosmallonions.api.images;

import java.io.InputStream;
import java.net.URL;

public interface ImageUploader {
    void uploadObject(InputStream inputStream, long size, String object, String bucket);
    void uploadObject(byte[] body, String object, String bucket);
    URL getObjectUri(String bucket, String path);
}
