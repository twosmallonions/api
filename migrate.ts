import path from 'node:path';
import { promises as fs } from 'node:fs';
import {
    FileMigrationProvider,
    Kysely,
    Migrator,
    PostgresDialect,
} from 'kysely';
import { Pool } from 'pg';

async function migrateToLatest() {
    const db = new Kysely<unknown>({
        dialect: new PostgresDialect({
            pool: new Pool({
                host: 'localhost',
                database: 'postgres',
                user: 'postgres',
                password: 'postgres'
            }),
        }),
    });

    const migrator = new Migrator({
        db,
        provider: new FileMigrationProvider({
            fs,
            path,
            migrationFolder: path.join(__dirname, 'migrations'),
        }),
    });

    const { error, results } = await migrator.migrateToLatest();

    results?.forEach((it) => {
        if (it.status === 'Success') {
            console.log(
                `migration "${it.migrationName}" was executed successfully`
            );
        } else if (it.status === 'Error') {
            console.error(`failed to execute migration "${it.migrationName}"`);
        }
    });

    if (error) {
        console.error('failed to migrate');
        console.error(error);
        process.exit(1);
    }

    await db.destroy();
}

migrateToLatest()
