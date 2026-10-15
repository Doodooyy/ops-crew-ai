import { drizzle } from 'drizzle-orm/better-sqlite3';
import Database from 'better-sqlite3';
import * as schema from './schema';

let _db: ReturnType<typeof drizzle> | null = null;

export function getDb(dbPath: string = '../backend/data/ops_crew.db') {
  if (!_db) {
    const sqlite = new Database(dbPath);
    _db = drizzle(sqlite, { schema });
  }
  return _db;
}

export * from './schema';
