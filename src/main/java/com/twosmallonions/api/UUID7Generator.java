package com.twosmallonions.api;

import com.fasterxml.uuid.Generators;
import org.hibernate.engine.spi.SharedSessionContractImplementor;
import org.hibernate.generator.BeforeExecutionGenerator;
import org.hibernate.generator.EventType;
import org.hibernate.generator.EventTypeSets;
import org.hibernate.id.IdentifierGenerator;

import java.io.Serializable;
import java.util.EnumSet;

public class UUID7Generator implements BeforeExecutionGenerator {
    @Override
    public Serializable generate(SharedSessionContractImplementor session, Object owner, Object currentValue, EventType eventType) {
        return Generators.timeBasedEpochGenerator().generate();
    }

    @Override
    public EnumSet<EventType> getEventTypes() {
        return EventTypeSets.INSERT_ONLY;
    }
}
