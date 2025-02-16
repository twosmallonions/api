import { and, eq } from 'drizzle-orm';
import { NodePgDatabase } from 'drizzle-orm/node-postgres';
import { instructions, recipes } from '../db/schema.js';
import { FullRecipe, FullRecipeSchema, RecipeInstruction } from '../types/recipe.js';
import { CreateRecipeSchema } from '../server.js';
import { instanceToInstance, plainToClass, plainToInstance } from 'class-transformer';

export class RecipeService {
    private db: NodePgDatabase;

    constructor(db: NodePgDatabase) {
        this.db = db;
    }

    async getFullRecipeBySlug(slug: string, user: string): Promise<FullRecipe> {
        const result = await this.db
            .select()
            .from(recipes)
            .leftJoin(instructions, eq(instructions.recipe, recipes.id))
            .where(and(eq(recipes.user, user), eq(recipes.slug, slug)));
        console.log(result);
        const recipe = {
            ...result[0].recipes,
            instructions: []
        } as FullRecipe;

        return FullRecipeSchema.parse(recipe);
    }

    async createRecipe(recipe: CreateRecipeSchema, user: string): Promise<FullRecipe> {
        const slug = 'asd';
        await this.db.insert(recipes).values({...recipe, user, slug}).returning({slug: recipes.slug})
        return this.getFullRecipeBySlug(slug, user);
    }
}
