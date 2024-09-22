package com.twosmallonions.api.recipe;

import org.springframework.data.repository.CrudRepository;

import java.util.List;
import java.util.Optional;
import java.util.UUID;

public interface RecipeRepository extends CrudRepository<Recipe, UUID> {
    <T> Optional<T> findByIdAndSubject(UUID uuid, String subject);
    List<Recipe> findBySubject(String subject);

    Optional<Recipe> findBySlugAndSubject(String slug, String subject);
}
