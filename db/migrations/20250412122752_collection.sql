-- migrate:up
CREATE TABLE tso.collections (
    id UUID PRIMARY KEY,
    name VARCHAR(500) NOT NULL CHECK (length(name) > 0),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TRIGGER tso_collection_update_updated_at BEFORE UPDATE
  ON tso.collections
  FOR EACH ROW
  EXECUTE FUNCTION tso.update_updated_at();

GRANT INSERT, SELECT, UPDATE, DELETE ON tso.collections TO tso_api_user;


CREATE TABLE tso.collection_members (
    collection UUID NOT NULL REFERENCES tso.collections (id) ON DELETE CASCADE ON UPDATE CASCADE,
    "user" UUID NOT NULL REFERENCES tso.users (id) ON DELETE CASCADE ON UPDATE CASCADE,
    owner boolean NOT NULL DEFAULT false,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (collection, "user")
);
GRANT INSERT, SELECT, UPDATE, DELETE ON tso.collection_members TO tso_api_user;

CREATE FUNCTION tso.new_collection_ensure_owner() RETURNS trigger
AS $$
BEGIN
  IF COUNT(*) = 0 FROM tso.collection_members AS cm WHERE cm.collection = NEW.id AND cm.owner = true THEN
    RAISE EXCEPTION 'collection %I does not have any members', NEW.id USING ERRCODE = 23514;
  END IF;

  RETURN new;
END;
$$ 
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = tso;

CREATE CONSTRAINT TRIGGER insert_collection_ensure_owner AFTER INSERT 
  ON tso.collections
  DEFERRABLE INITIALLY DEFERRED
  FOR EACH ROW
  EXECUTE FUNCTION tso.new_collection_ensure_owner();

-- policy functions
CREATE FUNCTION tso.current_user_is_collection_member(collection_id UUID) RETURNS BOOLEAN
AS $$
BEGIN
  RETURN collection_id IN (SELECT collection FROM tso.collection_members WHERE "user" = tso.get_current_user_id());
END;
$$
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = tso;

CREATE FUNCTION tso.current_user_is_collection_owner(collection_id UUID) RETURNS BOOLEAN
AS $$
BEGIN
  RETURN (collection_id IN (SELECT collection FROM tso.collection_members WHERE "user" = tso.get_current_user_id() AND owner = true));
END;
$$
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = tso;

CREATE FUNCTION tso.collection_has_no_members(collection_id UUID) RETURNS BOOLEAN
AS $$
BEGIN
  RETURN COUNT(*) = 0 FROM tso.collection_members WHERE collection = collection_id;
END;
$$
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = tso;

-- RLS collections table
ALTER TABLE tso.collections ENABLE ROW LEVEL SECURITY;

CREATE POLICY allow_read_for_collection_members ON tso.collections
FOR SELECT
USING (
  id IN (
    SELECT "collection"
    FROM tso.collection_members
    WHERE "user" = tso.get_current_user_id()
  )
);

CREATE POLICY allow_update_for_collection_members ON tso.collections
FOR UPDATE
USING (tso.current_user_is_collection_owner(id));

CREATE POLICY allow_write_collections ON tso.collections
FOR INSERT
WITH CHECK (true);

-- RLS collection_members table
ALTER TABLE tso.collection_members ENABLE ROW LEVEL SECURITY;

CREATE POLICY allow_read_for_collection_members ON tso.collection_members
FOR SELECT
USING (tso.current_user_is_collection_member(collection));

CREATE POLICY allow_insert ON tso.collection_members
FOR INSERT
WITH CHECK (tso.collection_has_no_members(collection) OR tso.current_user_is_collection_owner(collection));

-- migrate:down
