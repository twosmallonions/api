import express, { NextFunction, Request, Response } from 'express';
import { UnauthorizedError, expressjwt as jwt } from 'express-jwt';
import { expressJwtSecret } from 'jwks-rsa';
import { z, ZodError } from 'zod';
import { v4 } from 'uuid';
import { getDb } from './db/db.js';
import { RecipeService } from './services/RecipeService.js';
import { migrate } from 'drizzle-orm/node-postgres/migrator';
import 'reflect-metadata';

const app = express();

const db = getDb('postgresql://postgres:postgres@localhost:5432/postgres');
await migrate(db, {migrationsFolder: "schema"});
const recipeService = new RecipeService(db);
app.use(
    jwt({
        // @ts-expect-error wrong type
        secret: expressJwtSecret({
            cache: true,
            rateLimit: true,
            jwksRequestsPerMinute: 1,
            jwksUri:
                'https://auth-ng.meschter.me/realms/tso_dev/protocol/openid-connect/certs',
        }),
        //audience: 'tso-api',
        issuer: 'https://auth-ng.meschter.me/realms/tso_dev',
        algorithms: ['RS256', 'ES256'],
    })
);


app.use(express.json())

const port = 3000;

const createRecipeSchema = z.object({
    title: z.string().min(1).max(1000),
    description: z.string().optional()
});

export type CreateRecipeSchema = z.infer<typeof createRecipeSchema>;
app.post('/', async (req, res, next) => {
    const createRecipe = createRecipeSchema.parse(req.body);

    const recipe = await recipeService.createRecipe(createRecipe, v4());

    res.json(recipe)

});

// eslint-disable-next-line @typescript-eslint/no-unused-vars
app.use((err: Error, req: Request, res: Response, next: NextFunction) => {
    if (err instanceof UnauthorizedError) {
        console.error(`jwt verification failed: ${err.code}`);
        res.setHeader(
            'WWW-Authenticate',
            `Bearer error=${err.code} error_description=${err.message}`
        );
        res.status(401).send();
        return;
    }

    if (err instanceof z.ZodError) {
        res.status(400).json(err);
        return;
    }
    console.error(err.stack);
    res.status(500).send('something broke!');
});

app.listen(port, () => {
    console.log(`api listening on port ${port}`);
});
