CREATE TYPE measurement_system AS ENUM ('METRIC', 'IMPERIAL');

CREATE TABLE ingredients (
    id UUID NOT NULL PRIMARY KEY,
    notes VARCHAR(700),
    heading BOOLEAN NOT NULL,
    parsed_ingredient VARCHAR(600),
    parsed_original_amount DOUBLE PRECISION,
    parsed_original_unit VARCHAR(250),
    original_measurement_system measurement_system,

    parsed_converted_amount DOUBLE PRECISION,
    parsed_converted_unit VARCHAR(250),
    parsed_converted_measurement_system measurement_system,

    recipe_id UUID NOT NULL REFERENCES recipe (id) ON DELETE CASCADE,
    order_idx INT NOT NULL,
    UNIQUE (recipe_id, order_idx) DEFERRABLE INITIALLY DEFERRED
);

CREATE INDEX ingredients_recipe_id ON ingredients (recipe_id);