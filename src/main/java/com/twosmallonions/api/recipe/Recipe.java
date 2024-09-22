package com.twosmallonions.api.recipe;

import com.twosmallonions.api.UUIDv7Sequence;
import com.twosmallonions.api.images.ImageFile;
import com.twosmallonions.api.images.ImageTarget;
import com.twosmallonions.api.images.RecipeImage;
import com.twosmallonions.api.ingredients.Ingredient;
import com.twosmallonions.api.steps.Step;
import jakarta.persistence.*;
import lombok.*;
import org.hibernate.annotations.Generated;
import org.hibernate.proxy.HibernateProxy;

import java.time.ZonedDateTime;
import java.util.*;

@Entity
@Table(name = "recipe")
@NoArgsConstructor
@Getter
@Setter
public class Recipe implements ImageTarget {
    @Id
    @UUIDv7Sequence
    private UUID id;
    @Column(nullable = false)
    private String subject;
    @Column(nullable = false)
    private String slug;
    @Column(nullable = false)
    private String title;
    private String description;
    private String servings;
    @Column(name = "original_url")
    private String originalUrl;
    @Column(insertable = false, updatable = false, nullable = false)
    @Generated
    private ZonedDateTime added;
    @Column(insertable = false)
    @Generated
    private ZonedDateTime modified;
    @Column(name = "last_made")
    private ZonedDateTime lastMade;
    @Column(name = "prep_time")
    private Integer prepTime;
    @Column(name = "cook_time")
    private Integer cookTime;
    @Column(name = "rest_time")
    private Integer restTime;
    @Column(insertable = false, updatable = false, name = "total_time")
    @Generated()
    private Integer totalTime;
    private String note = "";
    @Column(insertable = false, updatable = false, nullable = false)
    private String image;

    private boolean liked = false;

    @Setter(AccessLevel.NONE)
    @OneToMany(mappedBy = "recipe", cascade = CascadeType.ALL, orphanRemoval = true)
    private List<Ingredient> ingredient = new ArrayList<>();

    @Setter(AccessLevel.NONE)
    @OneToMany(mappedBy = "recipe", cascade = CascadeType.ALL)
    @OrderBy("order_idx ASC")
    private List<Step> steps = new ArrayList<>();

    @Setter(AccessLevel.NONE)
    @OneToMany(mappedBy = "recipe", cascade = CascadeType.ALL)
    private List<RecipeImage> recipeImages = new ArrayList<>();

    @OneToOne()
    @JoinColumn(name = "cover_image")
    private RecipeImage coverImage;

    @PreUpdate
    protected void onUpdate() {
        modified = ZonedDateTime.now();
    }

    public void addIngredient(Ingredient ingredient) {
        this.ingredient.add(ingredient);
        ingredient.setRecipe(this);
    }

    public void removeIngredient(Ingredient ingredient) {
        this.ingredient.remove(ingredient);
        ingredient.setRecipe(null);
    }

    public void removeAllIngredients() {
        this.ingredient.clear();
    }

    public void removeAllSteps() {
        this.steps.clear();
    }

    public void addStep(Step step) {
        this.steps.add(step);
        step.setRecipe(this);
    }

    public void addImage(ImageFile image) {
        if (!(image instanceof RecipeImage recipeImage)) {
            throw new IllegalArgumentException("ImageFile image must be an instance of RecipeImage");
        }

        recipeImage.setRecipe(this);
        this.recipeImages.add(recipeImage);
        if (this.coverImage == null) {
            this.coverImage = recipeImage;
        }
    }

    @Override
    public final boolean equals(Object o) {
        if (this == o) return true;
        if (o == null) return false;
        Class<?> oEffectiveClass = o instanceof HibernateProxy ? ((HibernateProxy) o).getHibernateLazyInitializer().getPersistentClass() : o.getClass();
        Class<?> thisEffectiveClass = this instanceof HibernateProxy ? ((HibernateProxy) this).getHibernateLazyInitializer().getPersistentClass() : this.getClass();
        if (thisEffectiveClass != oEffectiveClass) return false;
        Recipe recipe = (Recipe) o;
        return getId() != null && Objects.equals(getId(), recipe.getId());
    }

    @Override
    public final int hashCode() {
        return this instanceof HibernateProxy ? ((HibernateProxy) this).getHibernateLazyInitializer().getPersistentClass().hashCode() : getClass().hashCode();
    }
}
