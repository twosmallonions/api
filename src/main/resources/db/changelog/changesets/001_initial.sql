CREATE TABLE recipe (
    id UUID PRIMARY KEY NOT NULL,
    subject VARCHAR NOT NULL,
    slug VARCHAR(50) NOT NULL,
    title VARCHAR NOT NULL,
    liked BOOLEAN NOT NULL,
    description VARCHAR,
    servings VARCHAR,
    original_url VARCHAR,
    added TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT current_timestamp,
    modified TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT current_timestamp,
    last_made TIMESTAMP WITH TIME ZONE,
    prep_time INTEGER,
    cook_time INTEGER,
    rest_time INTEGER,
    total_time INTEGER GENERATED ALWAYS AS (prep_time + cook_time + rest_time) STORED,
    note VARCHAR,
    image VARCHAR,
    UNIQUE (slug, subject)
);

CREATE INDEX recipe_subject_hash ON recipe USING hash (subject);
CREATE INDEX recipe_slug_hash ON recipe USING hash (slug);
CREATE INDEX recipe_subject_slug_hash ON recipe (subject, slug);
