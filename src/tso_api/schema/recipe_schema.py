import datetime
from uuid import UUID

from sqlalchemy import Column, DateTime, ForeignKey, String, Table, UniqueConstraint, text
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


collection_members = Table(
    'collection_member',
    Base.metadata,
    Column('collection_id', ForeignKey('collection.id'), primary_key=True),
    Column('user_id', ForeignKey('user.id'), primary_key=True),
    UniqueConstraint('collection_id', 'user_id'),
)


class UserSchema(AsyncAttrs, Base):
    __tablename__ = 'user'

    id: Mapped[UUID] = mapped_column(primary_key=True)
    subject: Mapped[str]
    issuer: Mapped[str]
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True))

    collections: Mapped[list['CollectionSchema']] = relationship(secondary=collection_members, back_populates='members')
    recipes: Mapped[list['RecipeSchema']] = relationship(back_populates='created_by')


class CollectionSchema(AsyncAttrs, Base):
    __tablename__ = 'collection'

    id: Mapped[UUID] = mapped_column(primary_key=True)
    name: Mapped[str]
    slug: Mapped[str]
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), default=datetime.datetime.now(datetime.UTC))
    update_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(True), default=datetime.datetime.now(datetime.UTC), onupdate=datetime.datetime.now(datetime.UTC)
    )

    members: Mapped[list[UserSchema]] = relationship(secondary=collection_members, back_populates='collections')

    assets: Mapped[list['AssetSchema']] = relationship(back_populates='collection')
    recipes: Mapped[list['RecipeSchema']] = relationship(back_populates='collection')


class AssetSchema(AsyncAttrs, Base):
    __tablename__ = 'asset'

    id: Mapped[UUID] = mapped_column(primary_key=True)
    path: Mapped[str] = mapped_column(String(4096))
    size: Mapped[int]
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), server_default=text('now()'))
    collection_id: Mapped[UUID] = mapped_column(ForeignKey('collection.id'))

    collection: Mapped[CollectionSchema] = relationship(back_populates='assets')


class RecipeSchema(AsyncAttrs, Base):
    __tablename__ = 'recipe'

    id: Mapped[UUID] = mapped_column(primary_key=True)
    collection_id: Mapped[UUID] = mapped_column(ForeignKey('collection.id'))
    title: Mapped[str]
    slug: Mapped[str]
    note: Mapped[str] = mapped_column(default='')
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), default=datetime.datetime.now(datetime.UTC))
    update_at: Mapped[datetime.datetime] = mapped_column(DateTime(True),
        default=datetime.datetime.now(datetime.UTC), onupdate=datetime.datetime.now(datetime.UTC)
    )
    created_by_id: Mapped[UUID] = mapped_column(ForeignKey('user.id'))
    cook_time: Mapped[int | None]
    prep_time: Mapped[int | None]
    recipe_yield: Mapped[str | None]
    last_made: Mapped[datetime.datetime]
    liked: Mapped[bool] = mapped_column(default=False)

    created_by: Mapped[UserSchema] = relationship(back_populates='recipes')
    instructions: Mapped[list['InstructionSchema']] = relationship(back_populates='recipe')
    ingredients: Mapped[list['IngredientSchema']] = relationship(back_populates='recipe')
    collection: Mapped[list[CollectionSchema]] = relationship(back_populates='recipes')
    __table_args__ = (UniqueConstraint('collection_id', 'slug'),)


class InstructionSchema(AsyncAttrs, Base):
    __tablename__ = 'instruction'

    id: Mapped[UUID] = mapped_column(primary_key=True)
    text: Mapped[str]
    recipe_id: Mapped[UUID] = mapped_column(ForeignKey('recipe.id'))
    position: Mapped[int]

    recipe: Mapped[RecipeSchema] = relationship(back_populates='instructions')

    __table_args__ = (UniqueConstraint('recipe_id', 'position'),)


class IngredientSchema(AsyncAttrs, Base):
    __tablename__ = 'ingredient'

    id: Mapped[UUID] = mapped_column(primary_key=True)
    text: Mapped[str]
    recipe_id: Mapped[UUID] = mapped_column(ForeignKey('recipe.id'))
    position: Mapped[int]

    recipe: Mapped[RecipeSchema] = relationship(back_populates='ingredients')

    __table_args__ = (UniqueConstraint('recipe_id', 'position'),)
