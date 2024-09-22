package com.twosmallonions.api.images;

import org.springframework.data.repository.CrudRepository;

import java.util.UUID;

public interface StepImageRepository extends CrudRepository<StepImage, UUID> {
}