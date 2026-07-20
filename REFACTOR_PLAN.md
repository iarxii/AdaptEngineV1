# AdaptEngineV1 - Refactor Roadmap (Updated)

## Phase 1: Structural Consolidation
- [x] Move `models.py` and `db_init.py` to `backend/app/core/`
- [x] Unify DB connection logic to use `sqlalchemy.ext.asyncio`
- [x] Update all imports to reference `backend.app.core`
- [x] Delete legacy root-level files (Consolidated logic moved to `/backend`)

## Phase 2: Performance & Async Optimization
- [ ] **Persistent Session:** Refactor `CrawlerWorker` to use a single shared `httpx.AsyncClient` instead of per-request instantiation.
- [ ] **Non-Blocking Embeddings:** Offload `SentenceTransformer.encode` to a thread pool using `asyncio.to_thread` to prevent Event Loop blocking.
- [ ] **Robustness:** Implement a retry mechanism (max 3 attempts) for transient network failures.
- [ ] **Connection Pooling:** Optimize `AsyncSession` lifecycle within the worker loop.

## Phase 3: Feature Integration (The "Loop")
- [x] Integrate `get_embedding` logic into the Crawler's `_index_page` method.
- [x] Implement automatic vectorization of crawled content.
- [ ] **Semantic Querying:** Implement `pgvector` cosine similarity search in the API layer.

## Phase 4: Validation
- [ ] Test end-to-end: Queue URL -> Crawl -> Embed -> Semantic Search.
- [ ] Verify Auth flow across the new structure.
- [ ] Load test: Verify API responsiveness while crawler is vectorizing heavy pages.
