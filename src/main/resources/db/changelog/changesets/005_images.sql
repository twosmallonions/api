CREATE TABLE recipe_image (
    id UUID NOT NULL PRIMARY KEY,
    recipe_id UUID NOT NULL REFERENCES recipe (id),
    uploaded timestamptz NOT NULL,
    formats text[] NOT NULL,
    full_path VARCHAR NOT NULL,
    full_path_thumbnail VARCHAR NOT NULL
);

CREATE INDEX recipe_image_recipe_id ON recipe_image (recipe_id);
ALTER TABLE recipe ADD COLUMN cover_image UUID REFERENCES recipe_image (id);

CREATE TABLE step_image (
    id UUID NOT NULL PRIMARY KEY,
    step_id UUID NOT NULL REFERENCES step (id),
    uploaded timestamptz NOT NULL,
    formats text[],
    full_path VARCHAR NOT NULL,
    full_path_thumbnail VARCHAR NOT NULL
);

CREATE INDEX step_image_step_id ON step_image (step_id);