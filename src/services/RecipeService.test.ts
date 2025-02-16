import { beforeAll, describe, test } from 'vitest';
import {
    PostgreSqlContainer,
    StartedPostgreSqlContainer,
} from '@testcontainers/postgresql';
import { migrate } from 'drizzle-orm/node-postgres/migrator';
import { v4 } from 'uuid';
import { NodePgDatabase } from 'drizzle-orm/node-postgres';
import { instructions, recipes } from '../db/schema.js';
import { getDb } from '../db/db.js';
import { RecipeService } from './RecipeService.js';

describe('RecipeService', () => {
    let db: NodePgDatabase;
    let container: StartedPostgreSqlContainer;
    let recipeService: RecipeService;
    beforeAll(async () => {
        container = await new PostgreSqlContainer('postgres:17').start();
        const psqlUri = `postgresql://${container.getUsername()}:${container.getPassword()}@${container.getHost()}:${container.getPort()}/${container.getDatabase()}`;
        db = getDb(psqlUri);
        await migrate(db, { migrationsFolder: 'schema' });
        recipeService = new RecipeService(db);
    });

    test('getRecipeFull', async ({ expect }) => {
        // setup
        const user = v4();
        const insertRecipe = (
            await db
                .insert(recipes)
                .values({ title: 'Test', user, slug: 'slug' })
                .returning()
        )[0];
        await db.insert(instructions).values({
            recipe: insertRecipe.id,
            position: 0,
            text: 'a test instruction',
        });
        await db.insert(instructions).values({
            recipe: insertRecipe.id,
            position: 1,
            text: 'a test instruction2',
        });

        // act
        const recipe = await recipeService.getFullRecipeBySlug('slug', user);

        // test
        expect(recipe).toMatchSnapshot();
    });
});
