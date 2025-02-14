import { and, eq } from "drizzle-orm";
import { instructions, recipes } from "../db/schema.js";
import { FullRecipe, RecipeInstruction } from "../types/recipe.js";
import { NodePgDatabase } from "drizzle-orm/node-postgres";

export class RecipeService {
    db: NodePgDatabase;

    constructor(db: NodePgDatabase) {
        this.db = db;
    }

    async getFullRecipeBySlug(slug: string, user: string): Promise<FullRecipe> {
        let result = (await this.db
                .select()
                .from(recipes)
                .innerJoin(instructions, eq(instructions.recipe, recipes.id))
                .where(
                    and(
                        eq(recipes.user, user),
                        eq(recipes.slug, slug)
                    )
                )
        );
        let recipe = {...result[0].recipes, instructions: result.map((instr): RecipeInstruction => ({
            ...instr.instructions
        }))}

        return recipe;
    }
}