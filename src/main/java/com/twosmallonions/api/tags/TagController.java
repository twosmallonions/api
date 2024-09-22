package com.twosmallonions.api.tags;

import com.twosmallonions.api.tags.dto.CreateTagDTO;
import com.twosmallonions.api.tags.dto.TagDTO;
import jakarta.validation.Valid;
import lombok.Getter;
import lombok.RequiredArgsConstructor;
import org.springframework.security.oauth2.server.resource.authentication.JwtAuthenticationToken;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/tag")
@RequiredArgsConstructor
public class TagController {
    private final TagService tagService;
    private final TagMapper tagMapper;

    @PostMapping
    public TagDTO createTag(@Valid @RequestBody CreateTagDTO createTagDTO, final JwtAuthenticationToken jwt) {
        var subject = (String) jwt.getTokenAttributes().get("sub");
        var tag = this.tagMapper.createTagToTag(createTagDTO, subject);
        var dbTag = this.tagService.saveTag(tag);
        return tagMapper.tagToTagDTO(dbTag);
    }

    @GetMapping
    public List<TagDTO> getTags(final JwtAuthenticationToken jwt) {
        var subject = (String) jwt.getTokenAttributes().get("sub");

        return tagService.getTagsByUser(subject).stream().map(tagMapper::tagToTagDTO).toList();
    }

    @PutMapping("/{id}")
    public TagDTO updateTag(final JwtAuthenticationToken jwt, @PathVariable int id, @Valid @RequestBody CreateTagDTO createTagDTO) {
        var subject = (String) jwt.getTokenAttributes().get("sub");

        var tag = this.tagService.updateTag(id, createTagDTO, subject);

        return tagMapper.tagToTagDTO(tag);
    }
}
