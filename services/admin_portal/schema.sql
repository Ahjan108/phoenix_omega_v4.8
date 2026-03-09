-- SQLite schema for Brand Admin Portal (minimal v1).
-- Run once to init DB; migrations out of scope for v1.

-- Admins (email from Cloudflare Access; bootstrap from config).
CREATE TABLE IF NOT EXISTS brand_admin_users (
  id TEXT PRIMARY KEY,
  email TEXT UNIQUE NOT NULL,
  display_name TEXT,
  status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'disabled')),
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

-- Which brands each admin can see.
CREATE TABLE IF NOT EXISTS brand_admin_grants (
  id TEXT PRIMARY KEY,
  user_id TEXT NOT NULL REFERENCES brand_admin_users(id),
  brand_id TEXT NOT NULL,
  role TEXT NOT NULL DEFAULT 'admin' CHECK (role IN ('admin', 'viewer')),
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  UNIQUE(user_id, brand_id)
);

CREATE INDEX IF NOT EXISTS idx_grants_user ON brand_admin_grants(user_id);
CREATE INDEX IF NOT EXISTS idx_grants_brand ON brand_admin_grants(brand_id);

-- Weekly packet metadata (synced from pipeline / download_index).
CREATE TABLE IF NOT EXISTS weekly_packets (
  id TEXT PRIMARY KEY,
  week_key TEXT NOT NULL,
  brand_id TEXT NOT NULL,
  r2_key TEXT NOT NULL,
  release_day TEXT,
  bytes INTEGER,
  sha256 TEXT,
  status TEXT NOT NULL DEFAULT 'ready' CHECK (status IN ('ready', 'missing', 'archived')),
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  UNIQUE(week_key, brand_id)
);

CREATE INDEX IF NOT EXISTS idx_packets_week ON weekly_packets(week_key);
CREATE INDEX IF NOT EXISTS idx_packets_brand ON weekly_packets(brand_id);

-- Audit: every list/mint/download_click.
CREATE TABLE IF NOT EXISTS packet_access_audit (
  id TEXT PRIMARY KEY,
  user_id TEXT,
  brand_id TEXT,
  week_key TEXT,
  action TEXT NOT NULL CHECK (action IN ('list', 'mint_link', 'download_click')),
  ip TEXT,
  user_agent TEXT,
  result TEXT NOT NULL DEFAULT 'ok' CHECK (result IN ('ok', 'denied', 'error')),
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_audit_user ON packet_access_audit(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_created ON packet_access_audit(created_at);
