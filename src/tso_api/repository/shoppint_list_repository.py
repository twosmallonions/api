INSERT_SHOPPING_LIST_QUERY= """INSERT INTO
shopping_lists 
    (id, owner, title)
VALUES (%(id)s, %(owner)s, %(title)s)"""

INSERT_SHOPPING_LIST_ENTRY_QUERY = """INSERT INTO
list_entries 
    (id, name, note, shopping_list)
VALUES (%(id)s, %(name)s, %(note)s, %(shopping_list)s)"""

SELECT_SHOPPING_LISTS = """SELECT
l.id, l.owner, l.title, l.created_at, l.updated_at
FROM shopping_lists l
WHERE l.id = %(id)s AND l.owner = %(owner)s
"""

SELECT_SHOPPING_LISTS_WITH_ENTRIES = """SELECT
* FROM shopping_lists_with_entries led
WHERE led.id = %(id)s AND led.owner = %(owner)s
"""

UPDATE_ENTRY_SET_COMPLETED = """UPDATE 
list_entries SET completed = true
WHERE id = %(id)s AND owner = %(owner)s
"""
