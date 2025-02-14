export interface FullRecipe {
    id: string
    title: string
    slug: string
    description: string | null
    created_at: Date
    updated_at: Date
    instructions: RecipeInstruction[]
}

export interface RecipeInstruction {
    text: string
}