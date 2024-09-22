package com.twosmallonions.api.tags;

import org.springframework.data.repository.CrudRepository;

import java.util.List;
import java.util.Optional;

public interface TagRepository extends CrudRepository<Tag, Long> {
    List<Tag> findBySubject(String subject);
    Optional<Tag> findBySubjectAndId(String subject, Long id);
}
