from sqlalchemy import ARRAY, Boolean, Column, Computed, DateTime, ForeignKeyConstraint, Index, Integer, JSON, MetaData, PrimaryKeyConstraint, String, Table, Text, UniqueConstraint, Uuid, text

metadata = MetaData()


t_recipes_full = Table(
    'recipes_full', metadata,
    Column('id', Uuid),
    Column('collection', Uuid),
    Column('title', String),
    Column('slug', String),
    Column('created_at', DateTime(True)),
    Column('updated_at', DateTime(True)),
    Column('cook_time', Integer),
    Column('prep_time', Integer),
    Column('total_time', Integer),
    Column('yield', String),
    Column('last_made', DateTime(True)),
    Column('liked', Boolean),
    Column('created_by', Integer),
    Column('instructions', ARRAY(JSON())),
    Column('ingredients', ARRAY(JSON())),
    Column('cover_image', Uuid),
    Column('cover_thumbnail', Uuid)
)

t_recipes_lite = Table(
    'recipes_lite', metadata,
    Column('id', Uuid),
    Column('collection', Uuid),
    Column('slug', String),
    Column('title', String),
    Column('created_at', DateTime(True)),
    Column('updated_at', DateTime(True)),
    Column('liked', Boolean)
)

t_schema_migrations = Table(
    'schema_migrations', metadata,
    Column('version', String(128), primary_key=True),
    PrimaryKeyConstraint('version', name='schema_migrations_pkey')
)

t_users = Table(
    'users', metadata,
    Column('id', Integer, primary_key=True),
    Column('subject', String(1000), nullable=False),
    Column('issuer', String(1000), nullable=False),
    Column('created_at', DateTime(True), nullable=False, server_default=text('now()')),
    PrimaryKeyConstraint('id', name='users_pkey'),
    UniqueConstraint('subject', 'issuer', name='users_subject_issuer_key'),
    Index('users_issuer_idx', 'issuer'),
    Index('users_subject_idx', 'subject')
)

t_collections = Table(
    'collections', metadata,
    Column('id', Uuid, primary_key=True),
    Column('name', String(500), nullable=False),
    Column('slug', String(500), nullable=False),
    Column('owner', Integer, nullable=False),
    Column('created_at', DateTime(True), nullable=False, server_default=text('now()')),
    Column('updated_at', DateTime(True), nullable=False, server_default=text('now()')),
    ForeignKeyConstraint(['owner'], ['users.id'], ondelete='RESTRICT', onupdate='CASCADE', name='collections_owner_fkey'),
    PrimaryKeyConstraint('id', name='collections_pkey'),
    UniqueConstraint('slug', 'owner', name='collections_slug_owner_key'),
    Index('collections_owner_idx', 'owner')
)

t_assets = Table(
    'assets', metadata,
    Column('id', Uuid, primary_key=True),
    Column('path', String(4096), nullable=False),
    Column('size', Integer, nullable=False),
    Column('original_name', String(255)),
    Column('created_at', DateTime(True), nullable=False, server_default=text('now()')),
    Column('collection', Uuid, nullable=False),
    ForeignKeyConstraint(['collection'], ['collections.id'], ondelete='CASCADE', onupdate='CASCADE', name='assets_collection_fkey'),
    PrimaryKeyConstraint('id', name='assets_pkey')
)

t_collection_members = Table(
    'collection_members', metadata,
    Column('id', Integer, primary_key=True),
    Column('collection', Uuid, nullable=False),
    Column('user', Integer, nullable=False),
    ForeignKeyConstraint(['collection'], ['collections.id'], ondelete='CASCADE', onupdate='CASCADE', name='collection_members_collection_fkey'),
    ForeignKeyConstraint(['user'], ['users.id'], ondelete='CASCADE', onupdate='CASCADE', name='collection_members_user_fkey'),
    PrimaryKeyConstraint('id', name='collection_members_pkey'),
    UniqueConstraint('collection', 'user', name='collection_members_collection_user_key'),
    Index('collection_members_collection_idx', 'collection'),
    Index('collection_members_user_idx', 'user')
)

t_recipes = Table(
    'recipes', metadata,
    Column('id', Uuid, primary_key=True),
    Column('collection', Uuid, nullable=False),
    Column('title', String, nullable=False),
    Column('slug', String, nullable=False),
    Column('note', Text),
    Column('created_at', DateTime(True), nullable=False, server_default=text('now()')),
    Column('updated_at', DateTime(True), nullable=False, server_default=text('now()')),
    Column('created_by', Integer, nullable=False),
    Column('cook_time', Integer),
    Column('prep_time', Integer),
    Column('total_time', Integer, Computed('(COALESCE(cook_time, 0) + COALESCE(prep_time, 0))', persisted=True)),
    Column('yield', String),
    Column('last_made', DateTime(True)),
    Column('liked', Boolean, nullable=False, server_default=text('false')),
    Column('cover_image', Uuid),
    Column('cover_thumbnail', Uuid),
    ForeignKeyConstraint(['collection'], ['collections.id'], ondelete='CASCADE', onupdate='CASCADE', name='recipes_collection_fkey'),
    ForeignKeyConstraint(['cover_image'], ['assets.id'], ondelete='SET NULL', onupdate='CASCADE', name='recipes_cover_image_fkey'),
    ForeignKeyConstraint(['cover_thumbnail'], ['assets.id'], ondelete='SET NULL', onupdate='CASCADE', name='recipes_cover_thumbnail_fkey'),
    ForeignKeyConstraint(['created_by'], ['users.id'], ondelete='RESTRICT', onupdate='CASCADE', name='recipes_created_by_fkey'),
    PrimaryKeyConstraint('id', name='recipes_pkey'),
    UniqueConstraint('collection', 'slug', name='recipes_collection_slug_key')
)

t_ingredients = Table(
    'ingredients', metadata,
    Column('id', Uuid, primary_key=True),
    Column('text', Text, nullable=False),
    Column('recipe', Uuid, nullable=False),
    Column('position', Integer, nullable=False),
    ForeignKeyConstraint(['recipe'], ['recipes.id'], ondelete='CASCADE', onupdate='CASCADE', name='ingredients_recipe_fkey'),
    PrimaryKeyConstraint('id', name='ingredients_pkey'),
    UniqueConstraint('recipe', 'position', name='ingredients_recipe_position_key'),
    Index('ingredients_recipe_idx', 'recipe')
)

t_instructions = Table(
    'instructions', metadata,
    Column('id', Uuid, primary_key=True),
    Column('text', Text, nullable=False),
    Column('recipe', Uuid, nullable=False),
    Column('position', Integer, nullable=False),
    ForeignKeyConstraint(['recipe'], ['recipes.id'], ondelete='CASCADE', onupdate='CASCADE', name='instructions_recipe_fkey'),
    PrimaryKeyConstraint('id', name='instructions_pkey'),
    UniqueConstraint('recipe', 'position', name='instructions_recipe_position_key'),
    Index('instructions_recipe_idx', 'recipe')
)
