package com.twosmallonions.api.ingredients;

import com.twosmallonions.api.ingredients.dto.IngredientDTO;
import jakarta.persistence.*;
import lombok.*;
import org.hibernate.annotations.JdbcTypeCode;
import org.hibernate.type.SqlTypes;

import java.util.ArrayList;

@Entity
@Table(name = "ingredients")
@NoArgsConstructor
@AllArgsConstructor
@Getter
@Setter
@Builder
public class Ingredients {
    @Id
    @GeneratedValue(generator = "ingredient_seq")
    @SequenceGenerator(name = "ingredient_seq", sequenceName = "ingredients_id_seq", allocationSize = 1)
    private Long id;
    @JdbcTypeCode(SqlTypes.JSON)
    private ArrayList<IngredientDTO> ingredients = new ArrayList<>();
}
