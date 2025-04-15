-- migrate:up
CREATE ROLE tso_api_user;
CREATE SCHEMA tso;
GRANT usage ON SCHEMA tso TO tso_api_user;

ALTER DEFAULT PRIVILEGES 
  IN SCHEMA tso
  GRANT SELECT, INSERT, UPDATE
  ON TABLES
  TO tso_api_user;

CREATE FUNCTION tso.set_uid(user_id uuid) RETURNS VOID 
AS $$
BEGIN
    EXECUTE format('set local tso.user_id to %I', user_id);
END;
$$ LANGUAGE plpgsql;

CREATE FUNCTION tso.get_current_user_id() RETURNS uuid 
AS $$
BEGIN
    RETURN COALESCE(NULLIF(current_setting('tso.user_id', true), '')::uuid, UUID('00000000-0000-0000-0000-000000000000'));
END;
$$ LANGUAGE plpgsql;

CREATE FUNCTION tso.update_updated_at() RETURNS trigger
AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TABLE tso.account (
    id UUID PRIMARY KEY,
    subject TEXT NOT NULL,
    issuer TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (subject, issuer),
    CHECK (length(subject) > 0),
    CHECK (length(issuer) > 0)
);

CREATE TRIGGER tso_account_update_updated_at BEFORE UPDATE
    ON tso.account 
    FOR EACH ROW
    EXECUTE FUNCTION tso.update_updated_at();



CREATE INDEX ON tso.account USING hash (subject);
CREATE INDEX ON tso.account USING hash (issuer);
-- migrate:down
