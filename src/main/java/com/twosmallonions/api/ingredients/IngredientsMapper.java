package com.twosmallonions.api.ingredients;

import com.twosmallonions.api.ingredients.dto.CreateIngredientDTO;
import com.twosmallonions.api.ingredients.dto.IngredientDTO;
import org.mapstruct.Mapper;
import org.mapstruct.Mapping;
import org.mapstruct.MappingTarget;
import org.mapstruct.factory.Mappers;

import java.util.UUID;

@Mapper(componentModel = "spring")
public interface IngredientsMapper {
    IngredientsMapper INSTANCE = Mappers.getMapper(IngredientsMapper.class);

    @Mapping(source = "id", target = "id")
    IngredientDTO createIngredientDTOToIngredientDTO(CreateIngredientDTO createIngredientDTO, UUID id);
}
