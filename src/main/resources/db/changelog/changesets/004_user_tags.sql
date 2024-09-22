--changeset MariusMeschter:4
CREATE TABLE user_tags (
    id UUID PRIMARY KEY NOT NULL,
    text VARCHAR(30) NOT NULL,
    color VARCHAR(7) NOT NULL DEFAULT '#ff7f50',
    subject VARCHAR NOT NULL,
    CHECK ( color ~* '^#[a-f0-9]{6}$' )
);

CREATE TABLE recipe_user_tags (
    recipe_id UUID NOT NULL REFERENCES recipe (id) ON DELETE CASCADE,
    user_tag_id UUID NOT NULL REFERENCES user_tags (id) ON DELETE CASCADE,
    PRIMARY KEY (user_tag_id, recipe_id)
);

CREATE INDEX recipe_user_tags_recipe_id ON recipe_user_tags (recipe_id);

CREATE TABLE user_categories (
    id UUID PRIMARY KEY NOT NULL,
    text VARCHAR(64) NOT NULL,
    color VARCHAR(7) NOT NULL,
    subject VARCHAR NOT NULL,
    CHECK ( color ~* '^#[a-f0-9]{6}$' )
);

CREATE TABLE recipe_user_categories (
    recipe_id UUID NOT NULL REFERENCES recipe (id) ON DELETE CASCADE,
    user_categories_id UUID NOT NULL REFERENCES user_categories (id) ON DELETE CASCADE,
    PRIMARY KEY (user_categories_id, recipe_id)
);

CREATE INDEX recipe_user_categories_recipe_id ON recipe_user_categories (recipe_id);