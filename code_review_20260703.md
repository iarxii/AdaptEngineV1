# Code Review - AdaptEngineV1
**Date:** 2026-07-03
**Status:** Critical Improvements Needed

## 🚩 Critical Issues (Security & Stability)

### 1. SQL Injection (High Risk)
The project lacks proper input sanitization in database queries. Variables are concatenated directly into SQL strings.
- **Example:** In `crawler.php`, the `UPDATE` queries use variables directly.
- **Risk:** Malicious websites can inject SQL commands via `<title>` or `<meta>` tags to compromise the database.
- **Fix:** Implement **Prepared Statements** using `mysqli` or `PDO`.

### 2. Cross-Site Scripting (XSS) (High Risk)
The crawler stores raw HTML and metadata from external sources. If this data is rendered on a search results page without escaping, it leads to XSS.
- **Fix:** Use `htmlspecialchars()` when outputting content or a library like **HTML Purifier**.

### 3. Recursive Infinite Loop (Stability)
The `follow_links` function calls itself recursively. Given the nature of the web, this will inevitably lead to a **Stack Overflow** or exceed PHP's memory/execution limits.
- **Fix:** Replace recursion with an **Iterative Queue-based approach** (e.g., a `while` loop processing a URL list).

---

## ⚙️ Architectural & Logic Improvements

### 1. Memory Exhaustion
The `$already_crawled` and `$crawling` arrays are held in memory. This will crash the script as the index grows.
- **Fix:** Use the database `index` table to track "seen" URLs instead of PHP arrays.

### 2. Fragile JSON Construction
JSON is being built via string concatenation in `get_details()`. This breaks if the crawled content contains double quotes.
- **Fix:** Use `json_encode()` on a PHP associative array.

### 3. Error Handling
Heavy use of the `@` error suppression operator makes debugging impossible.
- **Fix:** Use `try-catch` blocks and a proper logging system.

### 4. Robots.txt Compliance
The crawler ignores `robots.txt`, which can lead to IP bans from target websites.
- **Fix:** Implement a check for `/robots.txt` before crawling a new domain.

---

## 🛠️ Summary Table

| Area | Current State | Recommended Action |
| :--- | :--- | :--- |
| **DB Access** | String concatenation | **Switch to Prepared Statements** |
| **Crawl Logic** | Recursive functions | **Switch to Iterative Queue** |
| **Data Format** | Manual JSON strings | **Use `json_encode()`** |
| **Scaling** | In-memory arrays | **Use DB for tracking crawled URLs** |
| **Frontend** | Basic HTML/JS | Move to structured MVC pattern |
