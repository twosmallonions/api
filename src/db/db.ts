import { drizzle } from "drizzle-orm/node-postgres";

console.log(process.env['TSO_DB_URL'])
export const db = drizzle(process.env['TSO_DB_URL'] ?? '');

export function getDb(uri: string) {
    return drizzle(uri);
}