package com.twosmallonions.api.images;

import com.twosmallonions.api.UUIDv7Sequence;
import com.twosmallonions.api.steps.Step;
import io.hypersistence.utils.hibernate.type.array.ListArrayType;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.JoinColumn;
import jakarta.persistence.ManyToOne;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;
import org.hibernate.annotations.Type;

import java.time.ZonedDateTime;
import java.util.List;
import java.util.UUID;

@Entity
@Getter
@Setter
@NoArgsConstructor
public class StepImage {
    @Id
    @UUIDv7Sequence
    private UUID id;

    @ManyToOne
    @JoinColumn(name = "step_id")
    private Step step;

    private ZonedDateTime uploaded;

    @Type(ListArrayType.class)
    private List<String> formats;
}
