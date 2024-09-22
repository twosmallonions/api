package com.twosmallonions.api.steps;

import com.twosmallonions.api.ingredients.dto.IngredientDTO;
import com.twosmallonions.api.steps.dto.StepsDTO;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.Id;
import jakarta.persistence.SequenceGenerator;
import lombok.*;
import org.hibernate.annotations.JdbcTypeCode;
import org.hibernate.type.SqlTypes;

@Entity
@Getter
@Setter
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class Steps {
    @Id
    @GeneratedValue(generator = "ingredient_seq")
    @SequenceGenerator(name = "ingredient_seq", sequenceName = "ingredients_id_seq", allocationSize = 1)
    private Long id;
    @JdbcTypeCode(SqlTypes.JSON)
    private StepsDTO[] steps;

}
