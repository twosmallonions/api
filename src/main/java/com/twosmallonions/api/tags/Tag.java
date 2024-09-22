package com.twosmallonions.api.tags;

import com.twosmallonions.api.recipe.Recipe;
import jakarta.persistence.*;
import lombok.*;

import java.util.HashSet;
import java.util.Set;
import java.util.UUID;

@Entity
@Table(name = "user_tags")
@NoArgsConstructor
@AllArgsConstructor
@Getter
@Setter
@Builder
public class Tag {
    @Id
    @GeneratedValue(generator = "tag_seq")
    @SequenceGenerator(name = "tag_seq", sequenceName = "user_tags_id_seq", allocationSize = 1)
    private Long id;
    @Column(nullable = false)
    private String text;
    @Column(nullable = false)
    private String color;
    @Column(nullable = false)
    private String subject;
    @Column(insertable = false, updatable = false, nullable = false)
    @Generated
    private UUID uuid;

    //@ManyToMany(mappedBy = "tags")
    //private Set<Recipe> recipes = new HashSet<>();
}
