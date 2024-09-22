package com.twosmallonions.api.ingredients;

import com.twosmallonions.api.UUIDv7Sequence;
import com.twosmallonions.api.recipe.Recipe;
import com.twosmallonions.api.steps.ingredient.StepIngredient;
import jakarta.persistence.*;
import lombok.*;
import org.hibernate.annotations.JdbcType;
import org.hibernate.dialect.PostgreSQLEnumJdbcType;
import org.hibernate.proxy.HibernateProxy;

import java.util.ArrayList;
import java.util.List;
import java.util.Objects;
import java.util.UUID;

@Entity
@Table(name = "ingredients")
@NoArgsConstructor
@Getter
@Setter
public class Ingredient {
    @Id
    @UUIDv7Sequence
    private UUID id;
    private String notes;
    private Boolean heading = false;

    @Column(name = "parsed_ingredient")
    private String parsedIngredient;

    @Column(name = "parsed_original_amount")
    private double parsedOriginalAmount;
    @Column(name = "parsed_original_unit")
    private String parsedOriginalUnit;
    @Enumerated
    @JdbcType(PostgreSQLEnumJdbcType.class)
    @Column(name = "original_measurement_system")
    private MeasurementSystem originalMeasurementSystem;

    @Column(name = "parsed_converted_amount")
    private double parsedConvertedAmount;
    @Column(name = "parsed_converted_unit")
    private String parsedConvertedUnit;
    @Enumerated
    @JdbcType(PostgreSQLEnumJdbcType.class)
    @Column(name = "parsed_converted_measurement_system")
    private MeasurementSystem convertedMeasurementSystem;

    @ManyToOne
    @JoinColumn(name = "recipe_id")
    private Recipe recipe;

    @Setter(AccessLevel.NONE)
    @OneToMany(mappedBy = "ingredient")
    private List<StepIngredient> stepIngredients = new ArrayList<>();

    @Column(name = "order_idx")
    private int orderIdx;

    public void addStepIngredient(StepIngredient stepIngredient) {
        this.stepIngredients.add(stepIngredient);
        stepIngredient.setIngredient(this);
    }

    @Override
    public final boolean equals(Object o) {
        if (this == o) return true;
        if (o == null) return false;
        Class<?> oEffectiveClass = o instanceof HibernateProxy ? ((HibernateProxy) o).getHibernateLazyInitializer().getPersistentClass() : o.getClass();
        Class<?> thisEffectiveClass = this instanceof HibernateProxy ? ((HibernateProxy) this).getHibernateLazyInitializer().getPersistentClass() : this.getClass();
        if (thisEffectiveClass != oEffectiveClass) return false;
        Ingredient that = (Ingredient) o;
        return getId() != null && Objects.equals(getId(), that.getId());
    }

    @Override
    public final int hashCode() {
        return this instanceof HibernateProxy ? ((HibernateProxy) this).getHibernateLazyInitializer().getPersistentClass().hashCode() : getClass().hashCode();
    }
}
