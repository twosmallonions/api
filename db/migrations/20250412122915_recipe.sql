-- migrate:up
CREATE TABLE tso.asset (
    id UUID PRIMARY KEY,
    path text NOT NULL CHECK (length(path) <= 4096),
    size INTEGER NOT NULL,
    original_name text,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    collection_id UUID NOT NULL REFERENCES tso.collection (id) ON DELETE RESTRICT ON UPDATE RESTRICT
);

CREATE INDEX ON tso.asset (collection_id);

CREATE TABLE tso.recipe (
    id uuid PRIMARY KEY,
    collection_id uuid NOT NULL REFERENCES tso.collection (id) ON DELETE RESTRICT ON UPDATE RESTRICT,
    title TEXT NOT NULL CHECK (length(title) > 0 AND length(title) < 300),
    note TEXT NOT NULL CHECK (length(title) < 6000),
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now(),
    created_by UUID NOT NULL REFERENCES tso.account (id) ON DELETE RESTRICT ON UPDATE RESTRICT,
    cook_time int,
    prep_time int,
    total_time int GENERATED ALWAYS AS (
        coalesce(cook_time, 0) + coalesce(prep_time, 0)
    ) STORED,
    yield TEXT CHECK(length(yield) < 100),
    last_made timestamptz,
    liked bool NOT NULL DEFAULT false,
    cover_image uuid REFERENCES tso.asset (id) ON DELETE SET NULL ON UPDATE RESTRICT,
    cover_thumbnail uuid REFERENCES tso.asset (id) ON DELETE SET NULL ON UPDATE RESTRICT
);

CREATE INDEX ON tso.recipe (collection_id);
CREATE INDEX ON tso.recipe (cover_image);
CREATE INDEX ON tso.recipe (cover_thumbnail);

ALTER TABLE tso.recipe ENABLE ROW LEVEL SECURITY;

CREATE POLICY allow_for_collection_member ON tso.recipe
FOR ALL
USING(collection_id IN (SELECT collection_id FROM tso.get_collections_for_user()));

CREATE FUNCTION tso.current_user_has_permission_for_recipe(target_recipe_id UUID) RETURNS BOOLEAN
AS $$
BEGIN
  RETURN COUNT(*) = 0 FROM tso.recipe WHERE id = target_recipe_id;
END;
$$
LANGUAGE plpgsql
SECURITY INVOKER
SET search_path = tso;

CREATE TABLE tso.instruction (
    id uuid PRIMARY KEY,
    text text NOT NULL,
    recipe_id uuid REFERENCES tso.recipe (
        id
    ) ON DELETE CASCADE ON UPDATE CASCADE NOT NULL,
    position int NOT NULL,
    UNIQUE (recipe_id, position) DEFERRABLE INITIALLY DEFERRED
);
CREATE INDEX ON tso.instruction (recipe_id);

ALTER TABLE tso.instruction ENABLE ROW LEVEL SECURITY;

CREATE POLICY allow_for_recipe_access ON tso.instruction
FOR ALL
USING(tso.current_user_has_permission_for_recipe(recipe_id));

CREATE TABLE tso.ingredient (
    id uuid PRIMARY KEY,
    text text NOT NULL,
    recipe_id uuid REFERENCES tso.recipe (
        id
    ) ON DELETE CASCADE ON UPDATE CASCADE NOT NULL,
    position int NOT NULL,
    UNIQUE (recipe_id, position) DEFERRABLE INITIALLY DEFERRED
);
CREATE INDEX ON tso.ingredient (recipe_id);

ALTER TABLE tso.ingredient ENABLE ROW LEVEL SECURITY;

CREATE POLICY allow_for_recipe_access ON tso.ingredient
FOR ALL
USING(tso.current_user_has_permission_for_recipe(recipe_id));
-- migrate:down

