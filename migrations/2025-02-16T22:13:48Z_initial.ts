/* eslint-disable @typescript-eslint/no-explicit-any */
import { Kysely, sql } from "kysely";

export async function up(db: Kysely<any>): Promise<void> {
    await db.schema
        .createTable('recipes')
        .addColumn('id', 'uuid', (col) => col.primaryKey())
        .addColumn('user', 'varchar', (col) => col.notNull())
        .addColumn('title', 'text', (col) => col.notNull())
        .addColumn('slug', 'varchar', (col) => col.notNull())
        .addColumn('description', 'text')
        .addColumn('created_at', 'timestamptz', (col) => col.notNull().defaultTo(sql`now()`))
        .addColumn('updated_at', 'timestamptz', (col) => col.notNull().defaultTo(sql`now()`))
        .execute()

    await db.schema
        .createTable('instructions')
        .addColumn('id', 'uuid', (col) => col.primaryKey())
        .addColumn('text', 'text', (col) => col.notNull())
        .addColumn('recipe', 'uuid', (col) => col
            .references('recipes.id')
            .onDelete('cascade')
            .onUpdate('cascade')
            .notNull()
        )
        .addColumn('position', 'integer', (col) => col.notNull())
        .addUniqueConstraint('recipe_position_unique', ['recipe', 'position'])
        .execute();
    
}

export async function down(db: Kysely<any>): Promise<void> {
    await db.schema.dropTable('instructions').execute()
    await db.schema.dropTable('recipes').execute()
}