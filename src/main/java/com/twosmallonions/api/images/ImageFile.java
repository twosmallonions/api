package com.twosmallonions.api.images;

import java.net.URI;
import java.time.ZonedDateTime;
import java.util.List;

public interface ImageFile {
    String getFullPath();
    String getFullThumbnailPath();
    void setFullPath(String fullPath);
    void setFullThumbnailPath(String fullThumbnailPath);
    default String getTemporaryPath() {
        return getFullPath() + ".tmp";
    }

    default String getFullPath(String extension) {
        return getFullPath() + "." + extension;
    }

    default String getFullThumbnailPath(String extension) {
        return getFullThumbnailPath() + "." + extension;
    }

    List<String> getFormats();

    void setUploaded(ZonedDateTime uploadDate);
}
