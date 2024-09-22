package com.twosmallonions.api.steps.ingredient;

import com.twosmallonions.api.UUIDv7Sequence;
import com.twosmallonions.api.ingredients.Ingredient;
import com.twosmallonions.api.steps.Step;
import jakarta.persistence.*;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

import java.util.UUID;


@Entity
@Getter
@Setter
@NoArgsConstructor
@Table(name = "step_ingredient")
public class StepIngredient {
    @Id
    @UUIDv7Sequence
    private UUID id;
    private boolean highlight;
    @Column(name = "highlight_start")
    private int highlightStart;
    @Column(name = "highlight_end")
    private int highlightEnd;

    @ManyToOne
    @JoinColumn(name = "ingredient_id")
    private Ingredient ingredient;

    @ManyToOne
    @JoinColumn(name = "step_id")
    private Step step;
}
