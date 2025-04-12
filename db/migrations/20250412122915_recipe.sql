-- migrate:up
CREATE TABLE tso.assets (
    id UUID PRIMARY KEY,
    path VARCHAR(4096) NOT NULL,
    size INTEGER NOT NULL,
    original_name VARCHAR(255),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    collection UUID NOT NULL REFERENCES tso.collections (id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE tso.recipes (
    id uuid PRIMARY KEY,
    collection uuid NOT NULL REFERENCES tso.collections (id) ON DELETE RESTRICT ON UPDATE CASCADE,
    title varchar NOT NULL,
    slug varchar NOT NULL,
    note text,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now(),
    created_by UUID NOT NULL REFERENCES tso.users (id) ON DELETE RESTRICT ON UPDATE CASCADE,
    cook_time int,
    prep_time int,
    total_time int GENERATED ALWAYS AS (
        coalesce(cook_time, 0) + coalesce(prep_time, 0)
    ) STORED,
    yield varchar,
    last_made timestamptz,
    liked bool NOT NULL DEFAULT false,
    cover_image uuid REFERENCES tso.assets (id) ON DELETE SET NULL ON UPDATE CASCADE,
    cover_thumbnail uuid REFERENCES tso.assets (id) ON DELETE SET NULL ON UPDATE CASCADE,
    UNIQUE (collection, slug),
    CHECK (length(title) > 0)
);

CREATE TABLE tso.instructions (
    id uuid PRIMARY KEY,
    text text NOT NULL,
    recipe uuid REFERENCES tso.recipes (
        id
    ) ON DELETE CASCADE ON UPDATE CASCADE NOT NULL,
    position int NOT NULL,
    UNIQUE (recipe, position) DEFERRABLE INITIALLY DEFERRED
);

CREATE INDEX ON tso.instructions (recipe);

CREATE TABLE tso.ingredients (
    id uuid PRIMARY KEY,
    text text NOT NULL,
    recipe uuid REFERENCES tso.recipes (
        id
    ) ON DELETE CASCADE ON UPDATE CASCADE NOT NULL,
    position int NOT NULL,
    UNIQUE (recipe, position) DEFERRABLE INITIALLY DEFERRED
);

CREATE INDEX ON tso.ingredients (recipe);
-- migrate:down

