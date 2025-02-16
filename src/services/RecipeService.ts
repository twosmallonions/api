import { v7 } from 'uuid';
import { Kysely } from 'kysely';
import { FullRecipe, FullRecipeSchema } from '../types/recipe';
import { DB } from '../db/types';
import { CreateRecipeSchema } from '../server';

export class RecipeService {
    private db: Kysely<DB>;

    constructor(db: Kysely<DB>) {
        this.db = db;
    }

    async getFullRecipeBySlug(slug: string, user: string): Promise<FullRecipe> {
        const result = await this.db
            .selectFrom('recipes as r')
            .leftJoin('instructions as i', 'i.recipe', 'r.id')
            .select([
                'i.text as instruction_text',
                'r.title',
                'r.slug',
                'r.description',
                'r.created_at',
                'r.updated_at',
            ])
            .where('r.slug', '=', slug)
            .where('r.user', '=', user)
            .execute();

        const recipe: FullRecipe = {
            ...result[0],
            instructions: result
                .filter((item) => item.instruction_text !== null)
                .map((item) => ({ text: item.instruction_text! })),
        };

        return FullRecipeSchema.parse(recipe);
    }

    async createRecipe(
        recipe: CreateRecipeSchema,
        user: string
    ): Promise<FullRecipe> {
        const slug = 'asd';
        await this.db
            .insertInto('recipes')
            .values({
                ...recipe,
                slug,
                user,
                id: v7()
            })
            .execute()
        return this.getFullRecipeBySlug(slug, user);
    }
}
