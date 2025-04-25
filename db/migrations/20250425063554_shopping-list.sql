-- Copyright 2025 Marius Meschter
-- SPDX-License-Identifier: AGPL-3.0-only

-- migrate:up
CREATE TABLE tso.shopping_list (
    id uuid PRIMARY KEY,
    title TEXT NOT NULL CHECK (length(title) > 0 AND length(title) < 250),
    collection_id UUID NOT NULL REFERENCES tso.collection ON UPDATE RESTRICT ON DELETE RESTRICT,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now()
);

ALTER TABLE tso.shopping_list ENABLE ROW LEVEL SECURITY;

CREATE POLICY allow_for_collection_members ON tso.shopping_list
FOR ALL
USING (collection_id IN (SELECT collection_id FROM tso.get_collections_for_user()));

CREATE TRIGGER tso_shopping_list_update_updated_at BEFORE UPDATE
  ON tso.recipe
  FOR EACH ROW
  EXECUTE FUNCTION tso.update_updated_at();

CREATE TABLE tso.list_entry (
    id uuid PRIMARY KEY,
    name TEXT NOT NULL CHECK (length(name) > 0 AND length(name) < 500),
    note TEXT NOT NULL DEFAULT '',
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now(),
    list_id uuid REFERENCES tso.shopping_list (id) ON DELETE RESTRICT ON UPDATE RESTRICT NOT NULL,
    completed boolean NOT NULL DEFAULT false,
    completed_at timestamptz
);

CREATE INDEX ON tso.list_entry (list_id);

CREATE FUNCTION tso.get_shopping_lists_for_user() RETURNS TABLE(list_id UUID)
AS $$ SELECT DISTINCT id FROM tso.shopping_list $$
LANGUAGE sql
SECURITY INVOKER
STABLE
SET search_path = tso;

ALTER TABLE tso.list_entry ENABLE ROW LEVEL SECURITY;
CREATE POLICY allow_when_list_visible ON tso.list_entry
FOR ALL
USING(list_id IN (SELECT list_id FROM tso.get_shopping_lists_for_user()));

CREATE TRIGGER tso_shopping_list_entry_update_updated_at BEFORE UPDATE
  ON tso.list_entry
  FOR EACH ROW
  EXECUTE FUNCTION tso.update_updated_at();

CREATE FUNCTION tso.set_completed_at_timestamp() RETURNS trigger
AS $$
BEGIN
    IF (TG_OP = 'UPDATE' AND OLD.completed = false AND NEW.completed = true) THEN
        NEW.completed_at = now();
    ELSIF (TG_OP = 'UPDATE' AND OLD.completed = true and NEW.completed = false) THEN
        NEW.completed_at = null;
    ELSIF (TG_OP = 'INSERT' AND NEW.completed = true) THEN
        NEW.completed_at = now();
    END IF;

    RETURN new;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER tso_shopping_list_entry_set_completed_at BEFORE INSERT OR UPDATE OF completed
    ON tso.list_entry
    FOR EACH ROW
    EXECUTE FUNCTION tso.set_completed_at_timestamp();

-- migrate:down
DROP TABLE list_entry;
DROP TABLE shopping_list;

-- migrate:down

