-- migrate:up
CREATE TABLE users (
    id UUID PRIMARY KEY,
    subject VARCHAR(1000) NOT NULL,
    issuer VARCHAR(1000) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (subject, issuer)
);

CREATE INDEX ON users USING hash (subject);
CREATE INDEX ON users USING hash (issuer);

CREATE TABLE collections (
    id UUID PRIMARY KEY,
    name VARCHAR(500) NOT NULL,
    slug VARCHAR(500) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE collection_members (
    id SERIAL PRIMARY KEY,
    collection UUID NOT NULL REFERENCES collections (id) ON DELETE CASCADE ON UPDATE CASCADE,
    "user" UUID NOT NULL REFERENCES users (id) ON DELETE CASCADE ON UPDATE CASCADE,
    UNIQUE (collection, "user")
);

CREATE INDEX ON collection_members (collection);
CREATE INDEX ON collection_members ("user");

CREATE TABLE assets (
    id UUID PRIMARY KEY,
    path VARCHAR(4096) NOT NULL,
    size INTEGER NOT NULL,
    original_name VARCHAR(255),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    collection UUID NOT NULL REFERENCES collections (id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE recipes (
    id uuid PRIMARY KEY,
    collection uuid NOT NULL REFERENCES collections (id) ON DELETE CASCADE ON UPDATE CASCADE,
    title varchar NOT NULL,
    slug varchar NOT NULL,
    note text,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now(),
    created_by UUID NOT NULL REFERENCES users (id) ON DELETE RESTRICT ON UPDATE CASCADE,
    cook_time int,
    prep_time int,
    total_time int GENERATED ALWAYS AS (
        coalesce(cook_time, 0) + coalesce(prep_time, 0)
    ) STORED,
    yield varchar,
    last_made timestamptz,
    liked bool NOT NULL DEFAULT false,
    cover_image uuid REFERENCES assets (id) ON DELETE SET NULL ON UPDATE CASCADE,
    cover_thumbnail uuid REFERENCES assets (id) ON DELETE SET NULL ON UPDATE CASCADE,
    UNIQUE (collection, slug)
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

CREATE INDEX ON instructions (recipe);

CREATE TABLE ingredients (
    id uuid PRIMARY KEY,
    text text NOT NULL,
    recipe uuid REFERENCES recipes (
        id
    ) ON DELETE CASCADE ON UPDATE CASCADE NOT NULL,
    position int NOT NULL,
    UNIQUE (recipe, position) DEFERRABLE INITIALLY DEFERRED
);

CREATE INDEX ON ingredients (recipe);

-- migrate:down
DROP TABLE ingredients;
DROP TABLE instructions;
DROP TABLE recipes;
DROP TABLE assets;
