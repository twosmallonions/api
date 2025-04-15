-- migrate:up
CREATE TABLE shopping_lists (
    id uuid PRIMARY KEY,
    owner TEXT NOT NULL,
    title TEXT NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE list_entries (
    id uuid PRIMARY KEY,
    name TEXT NOT NULL,
    note TEXT NOT NULL DEFAULT '',
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now(),
    shopping_list uuid REFERENCES shopping_lists (id) ON DELETE CASCADE ON UPDATE CASCADE NOT NULL,
    completed boolean NOT NULL DEFAULT false,
    completed_at timestamptz,
    owner TEXT NOT NULL
);

CREATE VIEW shopping_lists_with_entries AS
WITH list_entries_data AS (
  SELECT 
    e.shopping_list,
    COUNT(*) AS entries_count,
    array_agg(
      json_build_object(
        'id', e.id,
        'name', e.name,
        'note', e.note,
        'created_at', e.created_at,
        'updated_at', e.updated_at,
        'completed', e.completed,
        'completed_at', e.completed_at
      ) ORDER BY e.created_at
    ) AS entries_array
  FROM list_entries e
  GROUP BY e.shopping_list
)
SELECT 
  l.id, 
  l.owner, 
  l.title, 
  l.created_at, 
  l.updated_at,
  COALESCE(led.entries_array, '{}') AS entries,
  COALESCE(led.entries_count, 0) AS entries_num
FROM shopping_lists l
LEFT JOIN list_entries_data led ON l.id = led.shopping_list;
    
-- migrate:down
DROP TABLE list_entry;
DROP TABLE shopping_list;
