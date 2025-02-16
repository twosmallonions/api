import * as p from 'drizzle-orm/pg-core';
import { v7 } from 'uuid';

export const recipes = p.pgTable(
    'recipes',
    {
        id: p
            .uuid()
            .$default(() => v7())
            .primaryKey(),
        user: p.varchar().notNull(),
        title: p.varchar().notNull(),
        slug: p.varchar().notNull(),
        description: p.varchar(),
        created_at: p.timestamp({ withTimezone: true }).defaultNow().notNull(),
        updated_at: p
            .timestamp({ withTimezone: true })
            .defaultNow()
            .$onUpdate(() => new Date())
            .notNull(),
    },
    (table) => [
        p.index('slug_idx').on(table.slug),
        p.unique().on(table.slug, table.user),
    ]
);

//export type NewRecipe = typeof recipes.$inferInsert;

export const instructions = p.pgTable(
    'instructions',
    {
        id: p
            .uuid()
            .$default(() => v7())
            .primaryKey(),
        text: p.varchar().notNull(),
        recipe: p
            .uuid()
            .references(() => recipes.id)
            .notNull(),
        position: p.integer().notNull(),
    },
    (table) => [p.unique().on(table.recipe, table.position)]
);
export type NewInstruction = typeof instructions.$inferInsert;
