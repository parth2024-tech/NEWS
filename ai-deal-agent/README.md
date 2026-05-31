# AI Deal Agent

A 10-layer automated agent that scrapes, extracts, and verifies AI tool deals, free credits, and startup programs, notifying you via email (and eventually Telegram).

## Setup

1. **Install dependencies:**
   You can install dependencies manually or use the provided Makefile:
   ```bash
   make install
   ```

2. **Environment Variables:**
   Copy the example environment file and fill in your API keys:
   ```bash
   cp .env.example .env
   ```
   Required keys:
   - `SUPABASE_URL`
   - `SUPABASE_KEY`
   - `ANTHROPIC_API_KEY`
   - `FIRECRAWL_API_KEY`
   - `SENDGRID_API_KEY`
   - `EMAIL_FROM`
   - `EMAIL_TO`

3. **Supabase Schema Setup:**
   Execute the following SQL in your Supabase SQL editor to create the required table:
   ```sql
   CREATE TABLE deals (
       id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
       tool_name TEXT NOT NULL,
       plan_name TEXT NOT NULL,
       discount_type TEXT NOT NULL,
       value_usd NUMERIC,
       eligibility TEXT NOT NULL,
       claim_url TEXT NOT NULL,
       expiry_date DATE,
       verification_status TEXT NOT NULL,
       confidence_score INTEGER,
       source_type TEXT NOT NULL,
       first_seen TIMESTAMPTZ DEFAULT NOW(),
       last_confirmed TIMESTAMPTZ DEFAULT NOW(),
       consecutive_misses INTEGER DEFAULT 0,
       is_active BOOLEAN DEFAULT TRUE,
       region TEXT DEFAULT 'global'
   );
   ```

4. Run locally (Dry-run if keys are missing):
   ```bash
   python agent.py --phase 1
   ```

## Architecture Layers
- **Layer 1**: Cron Trigger + Watchdog
- **Layer 2**: Sources (Official Pages - Phase 1)
- **Layer 3**: Anti-Bot (Firecrawl API)
- **Layer 4**: Deduplication (Planned Phase 2)
- **Layer 5**: LLM Extraction Pass 1 (Claude 3.5 Sonnet)
- **Layer 6**: Live URL Verification (Planned Phase 3)
- **Layer 7**: LLM Verification Pass 2 (Planned Phase 3)
- **Layer 8**: Database (Supabase Postgres)
- **Layer 9**: Email Composition (SendGrid - Plaintext for Phase 1)
- **Layer 10**: Dual Delivery (Telegram - Planned Phase 3)
