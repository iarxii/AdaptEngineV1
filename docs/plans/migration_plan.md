# Transition Plan: PHP/MySQL $\rightarrow$ FastAPI/PostgreSQL
**Date:** 2026-07-03
**Objective:** Migrate AdaptEngineV1 from a synchronous PHP monolithic architecture to a high-performance, asynchronous Python-based architecture using FastAPI and PostgreSQL.

## 🎯 Architecture Vision
The goal is to move from a "script-based" crawler to a "service-based" crawler.
- **Backend:** FastAPI (Asynchronous endpoints for high concurrency).
- **Database:** PostgreSQL (Better indexing, JSONB support for crawled metadata).
- **Crawler:** `httpx` or `playwright` (Async crawling) instead of recursive PHP calls.
- **Task Queue:** Celery or RabbitMQ (To handle crawling jobs in the background).

---

## 🛠️ Migration Roadmap

### Phase 1: Infrastructure & Schema Design
- [ ] Setup PostgreSQL environment.
- [ ] Design a normalized schema (URL mappings, Page content, Site metadata).
- [ ] Create data migration scripts to move existing MySQL data to Postgres.

### Phase 2: Core API Development (FastAPI)
- [ ] Implement Search API endpoint (Replacing `search/index.php`).
- [ ] Implement Indexing API (For the crawler to push data).
- [ ] Setup Pydantic models for data validation.
- [ ] Implement FastAPI Dependency Injection for DB sessions (SQLAlchemy/Tortoise).

### Phase 3: The Async Crawler (The "Engine")
- [ ] Replace recursive PHP logic with an **Iterative Async Queue**.
- [ ] Implement `httpx` for non-blocking HTTP requests.
- [ ] Integrate a `robots.txt` parser.
- [ ] Implement a "Seen" cache using Redis or a Postgres Bloom filter.

### Phase 4: Frontend Integration
- [ ] Update the HTML/JS frontend to consume the FastAPI JSON endpoints.
- [ ] Replace PHP server-side rendering with a client-side fetch approach.

---

## ✅ Todo Task List

### 🟦 High Priority (Infrastructure)
- [ ] `task_1`: Initialize Python project environment (Poetry/Pipenv).
- [ ] `task_2`: Define SQLAlchemy models for the `index` table.
- [ ] `task_3`: Build a script to migrate data from MySQL $\rightarrow$ PostgreSQL.

### 🟨 Medium Priority (Logic)
- [ ] `task_4`: Create `/search` GET endpoint in FastAPI.
- [ ] `task_5`: Build the async crawler loop (Base functionality).
- [ ] `task_6`: Implement HTML parsing using `BeautifulSoup4` or `Selectolax`.

### 🟩 Low Priority (Optimization)
- [ ] `task_7`: Implement Redis for URL deduplication.
- [ ] `task_8`: Add Docker Compose for easy deployment (FastAPI, Postgres, Redis).
- [ ] `task_9`: Add Prometheus metrics for crawl speed and indexing rate.
