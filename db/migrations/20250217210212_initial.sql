-- migrate:up
CREATE TABLE recipes (
    id uuid PRIMARY KEY,
    owner varchar NOT NULL,
    title varchar NOT NULL,
    slug varchar NOT NULL,
    description TEXT,
    created_at timestamptz NOT NULL default now(),
    updated_at timestamptz NOT NULL default now(),
    UNIQUE (owner, slug)
);

CREATE TABLE instructions (
    id uuid PRIMARY KEY,
    text TEXT NOT NULL,
    recipe uuid REFERENCES recipes (id) ON DELETE CASCADE ON UPDATE CASCADE NOT NULL,
    position int NOT NULL,
    UNIQUE (recipe, position) DEFERRABLE INITIALLY DEFERRED
);

-- migrate:down
DROP TABLE instructions;
DROP TABLE recipes;

