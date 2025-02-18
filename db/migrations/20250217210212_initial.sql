-- migrate:up
CREATE TABLE recipes (
    id uuid PRIMARY KEY,
    owner varchar NOT NULL,
    title varchar NOT NULL,
    slug varchar NOT NULL,
    description text,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now(),
    cook_time int,
    prep_time int,
    total_time int GENERATED ALWAYS AS (
        coalesce(cook_time, 0) + coalesce(prep_time, 0)
    ) STORED,
    yield varchar,
    last_made timestamptz,
    UNIQUE (owner, slug)
);

CREATE TABLE instructions (
    id uuid PRIMARY KEY,
    text text NOT NULL,
    recipe uuid REFERENCES recipes (
        id
    ) ON DELETE CASCADE ON UPDATE CASCADE NOT NULL,
    position int NOT NULL,
    UNIQUE (recipe, position) DEFERRABLE INITIALLY DEFERRED
);

CREATE TABLE ingredients (
    id uuid PRIMARY KEY,
    text text NOT NULL,
    recipe uuid REFERENCES recipes (
        id
    ) ON DELETE CASCADE ON UPDATE CASCADE NOT NULL,
    position int NOT NULL,
    UNIQUE (recipe, position) DEFERRABLE INITIALLY DEFERRED
);

-- migrate:down
DROP TABLE instructions;
DROP TABLE recipes;
