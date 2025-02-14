import { eq } from "drizzle-orm";
import { db } from "../db.js";
import { NewRecipe, recipes } from "../schema.js";

export async function findRecipeBySlug(slug: string) {
    return (await db
            .select()
            .from(recipes)
            .where(eq(recipes.slug, slug))
            .limit(1))[0]
}

export async function createRecipe(recipe: NewRecipe) {
    return (await db.insert(recipes).values(recipe).returning())[0];
}