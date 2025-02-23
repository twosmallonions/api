-- migrate:up
CREATE TABLE assets (
  id uuid PRIMARY KEY,
  path varchar(4096) NOT NULL,
  size integer NOT NULL,
  original_name varchar(255),
  created_at timestamptz NOT NULL DEFAULT now()
);

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
    liked bool NOT NULL DEFAULT false,
    cover_image uuid REFERENCES assets (id) ON DELETE SET NULL ON UPDATE CASCADE,
    cover_thumbnail uuid REFERENCES assets (id) ON DELETE SET NULL ON UPDATE CASCADE,
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

CREATE VIEW recipes_full AS
SELECT
    r.id,
    r.owner,
    r.title,
    r.slug,
    r.description,
    r.created_at,
    r.updated_at,
    r.cook_time,
    r.prep_time,
    r.total_time,
    r.yield,
    r.last_made,
    r.liked,
    (
        SELECT
            array_agg(
                json_build_object('text', ins.text, 'id', ins.id)
                ORDER BY ins.position
            )
        FROM instructions AS ins
        WHERE ins.recipe = r.id
    ) AS instructions,
    (
        SELECT
            array_agg(
                json_build_object('text', ing.text, 'id', ing.id)
                ORDER BY ing.position
            )
        FROM ingredients AS ing
        WHERE ing.recipe = r.id
    ) AS ingredients,
    ( SELECT assets.path FROM assets WHERE assets.id = r.cover_image ) AS cover_image,
    ( SELECT assets.path FROM assets WHERE assets.id = r.cover_thumbnail ) AS cover_thumbnail
FROM recipes AS r;
-- migrate:down
DROP TABLE instructions;
DROP TABLE recipes;
