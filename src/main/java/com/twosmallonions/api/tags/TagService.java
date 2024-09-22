package com.twosmallonions.api.tags;

import com.twosmallonions.api.exceptions.ResourceNotFoundException;
import com.twosmallonions.api.tags.dto.CreateTagDTO;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.UUID;

@Service
@RequiredArgsConstructor
public class TagService {
    private final TagRepository tagRepository;
    private final TagMapper tagMapper;

    public Tag saveTag(Tag tag) {
        return this.tagRepository.save(tag);
    }

    public List<Tag> getTagsByUser(String subject) {
        return this.tagRepository.findBySubject(subject);
    }

    public Tag updateTag(UUID id, CreateTagDTO createTagDTO, String subject) {
        var tag = this.getTag(id, subject);

        this.tagMapper.updateTagFromCreateTagDTO(tag, createTagDTO);

        return this.tagRepository.save(tag);
    }

    public Tag getTag(UUID id, String subject) {
        var optionalTag = this.tagRepository.findByUuidAndSubject(id, subject);
        if (optionalTag.isEmpty()) {
            throw new ResourceNotFoundException("Failed to find tag with id " + id);
        }

       return optionalTag.get();
    }
}
