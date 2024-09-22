CREATE TABLE step (
    id UUID NOT NULL PRIMARY KEY,
    description VARCHAR(5000) NOT NULL,
    heading BOOLEAN NOT NULL,
    recipe_id UUID NOT NULL REFERENCES recipe (id),
    order_idx INTEGER NOT NULL,
    UNIQUE (recipe_id, order_idx) DEFERRABLE INITIALLY DEFERRED
);

CREATE TABLE step_ingredient (
    id UUID NOT NULL  PRIMARY KEY,
    highlight BOOLEAN NOT NULL,
    highlight_start INTEGER,
    highlight_end INTEGER,
    ingredient_id UUID NOT NULL REFERENCES ingredients (id),
    step_id UUID NOT NULL REFERENCES step (id),
    UNIQUE (step_id, highlight_start, highlight_end) DEFERRABLE INITIALLY DEFERRED
);

CREATE INDEX step_ingredients_ingredient_id ON step_ingredient (ingredient_id);
CREATE INDEX step_ingredients_step_id ON step_ingredient (step_id);
