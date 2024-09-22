package com.twosmallonions.api.recipe;

import org.springframework.data.repository.CrudRepository;

import java.util.Optional;

public interface RecipeRepository extends CrudRepository<Recipe, Long> {
    Optional<Recipe> findByIdAndSubject(long id, String subject);
}
