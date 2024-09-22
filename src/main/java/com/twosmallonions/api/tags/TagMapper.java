package com.twosmallonions.api.tags;

import com.twosmallonions.api.tags.dto.CreateTagDTO;
import com.twosmallonions.api.tags.dto.TagDTO;
import org.mapstruct.Mapper;
import org.mapstruct.Mapping;
import org.mapstruct.MappingTarget;

@Mapper(componentModel = "spring")
public interface TagMapper {
    Tag createTagToTag(CreateTagDTO createTagDTO, String subject);
    TagDTO tagToTagDTO(Tag tag);
    void updateTagFromCreateTagDTO(@MappingTarget Tag tag, CreateTagDTO createTagDTO);
}
