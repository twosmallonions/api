package com.twosmallonions.api.images;

import org.springframework.data.repository.CrudRepository;

import java.util.UUID;

public interface RecipeImageRepository extends CrudRepository<RecipeImage, UUID> {
}