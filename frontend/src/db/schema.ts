import { sqliteTable, text, integer, real } from 'drizzle-orm/sqlite-core';

/**
 * Users / Solopreneur business profile
 * Tracks core resources: cash, reputation, and bandwidth capacity
 */
export const users = sqliteTable('users', {
  id: integer('id').primaryKey({ autoIncrement: true }),
  username: text('username').notNull().default('Solo Operator'),
  cash: real('cash').notNull().default(5000.0),
  reputation: integer('reputation').notNull().default(50),
  bandwidth: integer('bandwidth').notNull().default(10),
  maxBandwidth: integer('max_bandwidth').notNull().default(10),
  level: integer('level').notNull().default(1),
  createdAt: text('created_at').notNull(),
  updatedAt: text('updated_at').notNull(),
});

/**
 * Ledger / Cash Flow Transactions
 * Full audit trail of incomes, operational expenses, agent retainer fees, and rewards
 */
export const transactions = sqliteTable('transactions', {
  id: integer('id').primaryKey({ autoIncrement: true }),
  userId: integer('user_id').notNull().references(() => users.id),
  amount: real('amount').notNull(),
  type: text('type').notNull(), // 'income' | 'expense' | 'agent_fee' | 'reward' | 'penalty'
  description: text('description').notNull(),
  balanceAfter: real('balance_after').notNull(),
  createdAt: text('created_at').notNull(),
});

/**
 * Operational Agent Personas (CrewAI Agents)
 * Represents distinct AI specialized contractors hireable by the business
 */
export const agents = sqliteTable('agents', {
  id: text('id').primaryKey(), // e.g. 'auditor_stone', 'copywriter_clara', 'ops_commander_rex'
  name: text('name').notNull(),
  role: text('role').notNull(),
  title: text('title').notNull(),
  avatar: text('avatar').notNull(),
  status: text('status').notNull().default('idle'), // 'idle' | 'busy' | 'cooldown'
  hourlyRate: real('hourly_rate').notNull(),
  bandwidthCost: integer('bandwidth_cost').notNull(),
  specialties: text('specialties').notNull(), // JSON string array
  reputationRequired: integer('reputation_required').notNull().default(0),
});

/**
 * Paper Contracts / Operations Work Orders
 * Tasks executed by CrewAI agents or handled directly by the player
 */
export const contracts = sqliteTable('contracts', {
  id: integer('id').primaryKey({ autoIncrement: true }),
  title: text('title').notNull(),
  description: text('description').notNull(),
  category: text('category').notNull(), // 'finance' | 'ops' | 'growth' | 'compliance'
  priority: text('priority').notNull().default('medium'), // 'low' | 'medium' | 'high' | 'urgent'
  status: text('status').notNull().default('pending'), // 'pending' | 'in_progress' | 'completed' | 'failed'
  assignedAgentId: text('assigned_agent_id').references(() => agents.id),
  rewardCash: real('reward_cash').notNull(),
  rewardReputation: integer('reward_reputation').notNull(),
  bandwidthCost: integer('bandwidth_cost').notNull(),
  resultSummary: text('result_summary'),
  createdAt: text('created_at').notNull(),
  completedAt: text('completed_at'),
});

/**
 * Desk Memos & Audit Trail
 * Paper-themed logging of agent executions, stamps, alerts, and decisions
 */
export const deskMemos = sqliteTable('desk_memos', {
  id: integer('id').primaryKey({ autoIncrement: true }),
  taskId: integer('task_id').references(() => contracts.id),
  agentId: text('agent_id').references(() => agents.id),
  memoType: text('memo_type').notNull(), // 'memo' | 'stamp' | 'alert' | 'agent_thought'
  message: text('message').notNull(),
  metadata: text('metadata'), // JSON string
  timestamp: text('timestamp').notNull(),
});

export type User = typeof users.$inferSelect;
export type NewUser = typeof users.$inferInsert;
export type Transaction = typeof transactions.$inferSelect;
export type Agent = typeof agents.$inferSelect;
export type Contract = typeof contracts.$inferSelect;
export type DeskMemo = typeof deskMemos.$inferSelect;
