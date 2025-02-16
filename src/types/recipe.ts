import { z } from 'zod';
export const RecipeInstructionSchema = z.object({
    text: z.string(),
});

export const FullRecipeSchema = z.object({
    title: z.string(),
    slug: z.string(),
    description: z.string().nullable(),
    created_at: z.date(),
    updated_at: z.date(),
    instructions: z.array(RecipeInstructionSchema),
});

export type FullRecipe = z.infer<typeof FullRecipeSchema>;
export type RecipeInstruction = z.infer<typeof RecipeInstructionSchema>;
