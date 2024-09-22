package com.twosmallonions.api.images;

import com.fasterxml.uuid.Generators;
import com.twosmallonions.api.UUIDv7Sequence;
import com.twosmallonions.api.recipe.Recipe;
import io.hypersistence.utils.hibernate.type.array.ListArrayType;
import jakarta.persistence.*;
import jakarta.validation.constraints.NotNull;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;
import org.hibernate.annotations.Type;

import java.time.ZonedDateTime;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.UUID;

@Entity
@Getter
@Setter
public class RecipeImage implements ImageFile {

    @Id
    @UUIDv7Sequence
    private UUID id;

    @NotNull
    @ManyToOne
    @JoinColumn(name = "recipe_id")
    private Recipe recipe;

    @NotNull
    private ZonedDateTime uploaded = ZonedDateTime.now();

    @NotNull
    @Type(ListArrayType.class)
    private List<String> formats = Arrays.asList("avif", "jpg");

    @NotNull
    @Column(name = "full_path")
    private String fullPath;

    @NotNull
    @Column(name = "full_path_thumbnail")
    private String fullThumbnailPath;

    @OneToOne(mappedBy = "coverImage")
    private Recipe recipeCoverImage;

    public RecipeImage() {
        this.id = Generators.timeBasedEpochGenerator().generate();
    }
}
