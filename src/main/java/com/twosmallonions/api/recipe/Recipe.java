package com.twosmallonions.api.recipe;

import com.twosmallonions.api.ingredients.Ingredients;
import com.twosmallonions.api.steps.Steps;
import com.twosmallonions.api.tags.Tag;
import jakarta.persistence.*;
import lombok.*;
import org.hibernate.annotations.Generated;

import java.time.ZonedDateTime;
import java.util.HashSet;
import java.util.Set;
import java.util.UUID;

@Entity
@Table(name = "recipe")
@NoArgsConstructor
@AllArgsConstructor
@Getter
@Setter
@Builder
public class Recipe {
    @Id
    @GeneratedValue(generator = "recipe_seq")
    @SequenceGenerator(name = "recipe_seq", sequenceName = "recipe_id_seq", allocationSize = 1)
    private Long id;
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
    private String note;
    @Column(insertable = false, updatable = false, nullable = false)
    @Generated
    private UUID uuid;
    private String image;

    @OneToOne(cascade = CascadeType.ALL)
    @JoinColumn(name = "ingredients_id", referencedColumnName = "id")
    private Ingredients ingredients;

    @OneToOne(cascade = CascadeType.ALL)
    @JoinColumn(name = "steps_id", referencedColumnName = "id")
    private Steps steps;

    @ManyToMany(cascade = CascadeType.ALL)
    @JoinTable(
            name = "recipe_user_tags",
            joinColumns = @JoinColumn(name = "recipe_id"),
            inverseJoinColumns = @JoinColumn(name = "user_tag_id")
    )
    Set<Tag> tags = new HashSet<>();

    @PreUpdate
    protected void onUpdate() {
        modified = ZonedDateTime.now();
    }
}
