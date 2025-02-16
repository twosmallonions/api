import { drizzle } from 'drizzle-orm/node-postgres';
import { Kysely, PostgresDialect } from 'kysely';
import { Pool } from 'pg';
import { DB } from './types';

console.log(process.env['TSO_DB_URL']);
export const db = drizzle(process.env['TSO_DB_URL'] ?? '');

export function getDb(uri: string) {
    const db = new Kysely<DB>({
        dialect: new PostgresDialect({
            pool: new Pool({
                connectionString: uri,
            }),
        }),
    });

    return db;
}
