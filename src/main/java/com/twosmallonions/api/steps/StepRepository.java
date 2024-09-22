package com.twosmallonions.api.steps;

import org.springframework.data.repository.CrudRepository;

import java.util.UUID;

public interface StepRepository extends CrudRepository<Step, UUID> {
}
