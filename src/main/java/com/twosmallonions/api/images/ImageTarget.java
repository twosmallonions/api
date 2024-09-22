package com.twosmallonions.api.images;

import java.util.UUID;

public interface ImageTarget {
    void addImage(ImageFile image);
    UUID getId();
}
