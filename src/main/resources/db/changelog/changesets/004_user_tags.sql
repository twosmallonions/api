CREATE TABLE user_tags (
    id BIGSERIAL PRIMARY KEY,
    text VARCHAR(30) NOT NULL,
    color VARCHAR(7) NOT NULL DEFAULT '#ff7f50',
    subject VARCHAR NOT NULL,
    check ( color ~* '^#[a-f0-9]{6}$' )
);

CREATE TABLE recipe_user_tags (
    recipe_id BIGINT NOT NULL REFERENCES recipe (id) ON DELETE CASCADE,
    user_tag_id BIGINT NOT NULL REFERENCES user_tags (id) ON DELETE CASCADE,
    PRIMARY KEY (recipe_id, user_tag_id)
);

CREATE TABLE user_categories (
    id BIGSERIAL PRIMARY KEY,
    text VARCHAR(64) NOT NULL,
    color VARCHAR(7) NOT NULL,
    subject VARCHAR NOT NULL
    check ( color ~* '^#[a-f0-9]{6}$' )
);

CREATE TABLE recipe_user_categories (
    recipe_id BIGINT NOT NULL REFERENCES recipe (id) ON DELETE CASCADE,
    user_categories_id BIGINT NOT NULL REFERENCES user_categories (id) ON DELETE CASCADE,
    PRIMARY KEY (recipe_id, user_categories_id)
);