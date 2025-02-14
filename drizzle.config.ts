import { defineConfig } from 'drizzle-kit'

export default defineConfig({
    out: './schema',
    schema: './src/db/schema.ts',
    dialect: 'postgresql'
})