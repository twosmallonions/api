-- migrate:up
CREATE TABLE tso.collection (
    id UUID PRIMARY KEY,
    name TEXT NOT NULL CHECK (length(name) > 0),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TRIGGER tso_collection_update_updated_at BEFORE UPDATE
  ON tso.collection
  FOR EACH ROW
  EXECUTE FUNCTION tso.update_updated_at();

CREATE TABLE tso.collection_member (
    collection_id UUID NOT NULL REFERENCES tso.collection (id) ON DELETE CASCADE ON UPDATE CASCADE,
    account_id UUID NOT NULL REFERENCES tso.account (id) ON DELETE CASCADE ON UPDATE CASCADE,
    owner BOOLEAN NOT NULL DEFAULT false,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (collection_id, account_id)
);

CREATE FUNCTION tso.new_collection_ensure_owner() RETURNS trigger
AS $$
BEGIN
  IF COUNT(*) = 0 FROM tso.collection_member AS cm WHERE cm.collection_id = NEW.id AND cm.owner = true THEN
    RAISE EXCEPTION 'collection %I does not have any members', NEW.id USING ERRCODE = 23514;
  END IF;

  RETURN new;
END;
$$ 
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = tso;

CREATE CONSTRAINT TRIGGER insert_collection_ensure_owner AFTER INSERT 
  ON tso.collection
  DEFERRABLE INITIALLY DEFERRED
  FOR EACH ROW
  EXECUTE FUNCTION tso.new_collection_ensure_owner();

-- policy functions
CREATE FUNCTION tso.current_user_is_collection_member(target_collection_id UUID) RETURNS BOOLEAN
AS $$
BEGIN
  RETURN target_collection_id IN (SELECT collection_id FROM tso.collection_member WHERE account_id = tso.get_current_user_id());
END;
$$
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = tso;

CREATE FUNCTION tso.current_user_is_collection_owner(target_collection_id UUID) RETURNS BOOLEAN
AS $$
BEGIN
  RETURN (target_collection_id IN (SELECT collection_id FROM tso.collection_member WHERE account_id = tso.get_current_user_id() AND owner = true));
END;
$$
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = tso;

CREATE FUNCTION tso.collection_has_no_members(target_collection_id UUID) RETURNS BOOLEAN
AS $$
BEGIN
  RETURN COUNT(*) = 0 FROM tso.collection_member WHERE collection_id = target_collection_id;
END;
$$
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = tso;

-- RLS collections table
ALTER TABLE tso.collection ENABLE ROW LEVEL SECURITY;

CREATE POLICY allow_read_for_collection_members ON tso.collection
FOR SELECT
USING (tso.current_user_is_collection_member(id) OR tso.collection_has_no_members(id));

CREATE POLICY allow_update_for_collection_members ON tso.collection
FOR UPDATE
USING (tso.current_user_is_collection_owner(id));

CREATE POLICY allow_write_collections ON tso.collection
FOR INSERT
WITH CHECK (true);

-- RLS collection_members table
ALTER TABLE tso.collection_member ENABLE ROW LEVEL SECURITY;

CREATE POLICY allow_read_for_collection_members ON tso.collection_member
FOR SELECT
USING (tso.current_user_is_collection_member(collection_id));

CREATE POLICY allow_insert ON tso.collection_member
FOR INSERT
WITH CHECK (tso.collection_has_no_members(collection_id) OR tso.current_user_is_collection_owner(collection_id));

-- migrate:down
