package com.twosmallonions.api.tags;

import com.twosmallonions.api.exceptions.ResourceNotFoundException;
import com.twosmallonions.api.tags.dto.CreateTagDTO;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.util.List;

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

    public Tag updateTag(long tagId, CreateTagDTO createTagDTO, String subject) {
        var optionalTag = this.tagRepository.findBySubjectAndId(subject, tagId);
        if (optionalTag.isEmpty()) {
            throw new ResourceNotFoundException();
        }

        var tag = optionalTag.get();

        this.tagMapper.updateTagFromCreateTagDTO(tag, createTagDTO);

        return this.tagRepository.save(tag);
    }
}
