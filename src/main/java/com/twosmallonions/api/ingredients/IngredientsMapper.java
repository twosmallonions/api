package com.twosmallonions.api.ingredients;

import com.twosmallonions.api.ingredients.dto.CreateIngredientDTO;
import com.twosmallonions.api.ingredients.dto.IngredientDTO;
import org.mapstruct.*;
import org.mapstruct.factory.Mappers;

import java.util.Comparator;
import java.util.List;

@Mapper(
        componentModel = "spring",
        unmappedTargetPolicy = ReportingPolicy.ERROR
)
public interface IngredientsMapper {
    IngredientsMapper INSTANCE = Mappers.getMapper(IngredientsMapper.class);

    @Mapping(target = "id", ignore = true)
    @Mapping(target = "parsedConvertedAmount", ignore = true)
    @Mapping(target = "parsedConvertedUnit", ignore = true)
    @Mapping(target = "convertedMeasurementSystem", ignore = true)
    @Mapping(target = "recipe", ignore = true)
    @Mapping(target = "stepIngredients", ignore = true)
    Ingredient createIngredientDTOToIngredient(CreateIngredientDTO createIngredientDTO, int orderIdx);
    IngredientDTO ingredientToIngredientDTO(Ingredient ingredient);

    @Mapping(target = "parsedConvertedAmount", nullValuePropertyMappingStrategy = NullValuePropertyMappingStrategy.IGNORE)
    @Mapping(target = "parsedConvertedUnit", nullValuePropertyMappingStrategy = NullValuePropertyMappingStrategy.IGNORE)
    @Mapping(target = "convertedMeasurementSystem", nullValuePropertyMappingStrategy = NullValuePropertyMappingStrategy.IGNORE)
    @Mapping(target = "recipe", ignore = true)
    @Mapping(target = "stepIngredients", ignore = true)
    @Mapping(source = "id", target = "id", ignore = true)
    void updateIngredient(@MappingTarget Ingredient ingredient, IngredientDTO ingredientDTO);

    @Mapping(target = "recipe", ignore = true)
    @Mapping(target = "stepIngredients", ignore = true)
    Ingredient ingredientDTOToIngredient(IngredientDTO ingredientDTO, int order_idx);

    default List<IngredientDTO> sortedIngredientMapper(List<Ingredient> ingredients) {
        if (ingredients == null) {
            return null;
        }

        return ingredients.stream()
                .map(this::ingredientToIngredientDTO)
                .sorted(Comparator.comparingInt(IngredientDTO::getOrderIdx))
                .toList();
    }
}
