package com.twosmallonions.api.steps;

import com.twosmallonions.api.UUIDv7Sequence;
import com.twosmallonions.api.recipe.Recipe;
import com.twosmallonions.api.steps.dto.StepDTO;
import com.twosmallonions.api.steps.ingredient.StepIngredient;
import jakarta.persistence.*;
import lombok.*;
import org.hibernate.annotations.JdbcTypeCode;
import org.hibernate.type.SqlTypes;

import java.util.ArrayList;
import java.util.List;
import java.util.UUID;

@Entity
@Getter
@Setter
@NoArgsConstructor
public class Step {
    @Id
    @UUIDv7Sequence
    private UUID id;
    private String description;
    private boolean heading = false;
    private int order_idx;

    @ManyToOne
    @JoinColumn(name = "recipe_id")
    private Recipe recipe;

    @Setter(AccessLevel.NONE)
    @OneToMany(mappedBy = "step", cascade = CascadeType.ALL, orphanRemoval = true)
    private List<StepIngredient> stepIngredients = new ArrayList<>();

    public void addStepIngredient(StepIngredient stepIngredient) {
        this.stepIngredients.add(stepIngredient);
        stepIngredient.setStep(this);
    }
}
