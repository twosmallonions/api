import {assert, beforeAll, expect, test} from 'vitest';
import { db } from '../db.js';
import * as RecipeRepository from './RecipeRepository.js';
import { migrate } from 'drizzle-orm/node-postgres/migrator';
import { instructions, recipes } from '../schema.js';
import { eq } from 'drizzle-orm';
import {generate} from 'randomstring';

beforeAll(async () => {
    await migrate(db, {migrationsFolder: 'schema'})
})

test('add a new recipe', async () => {
    let createRecipe = await RecipeRepository.createRecipe({title: 'test', slug: generate(20)})
    let recipe = await RecipeRepository.findRecipeBySlug(createRecipe.slug);
    expect(recipe.title).to.equal('test');
})

test('add a new recipe with an instruction', async() => {
    let recipe = await RecipeRepository.createRecipe({title: 'test', slug: generate(20)});
    await db.insert(instructions).values({recipe: recipe.id, position: 0, text: 'a test instruction'})
    await db.insert(instructions).values({recipe: recipe.id, position: 1, text: 'a test instruction2'})

    const res = await db.select().from(recipes).innerJoin(instructions, eq(recipes.id, instructions.recipe)).where(eq(recipes.slug, recipe.slug));

    expect(res.length).to.equal(2);
})