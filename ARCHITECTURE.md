## AI Restaurant Recommendation Service – Architecture

This document describes the high-level architecture for an AI-powered Restaurant Recommendation Service that:
- Takes user preferences (price, place, rating, cuisine)
- Retrieves restaurant data from the Hugging Face dataset `ManikaSaini/zomato-restaurant-recommendation` via the Hugging Face API
- Calls an LLM to create clear, human-friendly restaurant recommendations
- Exposes an API (and optionally a simple UI) to clients

No implementation is included here; this is an architectural blueprint divided into phases.

---

## 1. High-Level System Overview

- **Client Layer**
  - Web UI or API client (e.g., web app, mobile app, Postman) that sends user preferences and receives recommendations.
- **Backend Service**
  - REST (or GraphQL) API that validates input, orchestrates data retrieval, filtering, LLM prompt construction, and response formatting.
- **Data Layer**
  - Integration with Hugging Face datasets API to access `ManikaSaini/zomato-restaurant-recommendation`.
  - Optional local cache / database to store preprocessed restaurant data and metadata.
- **AI Layer**
  - LLM integration (OpenAI, Anthropic, or Hugging Face Inference API, etc.) for natural language recommendation generation and ranking explanation.
  - Internal rule-based / scoring logic to pre-filter and rank restaurants before passing a subset to the LLM.
- **Observability & Operations**
  - Logging, metrics, and basic monitoring of API usage, latency, and LLM costs.

Data flow (simplified):
1. Client sends preferences → Backend API
2. Backend queries local cache or Hugging Face dataset for candidate restaurants
3. Backend filters & ranks candidates
4. Backend constructs structured prompt, calls LLM
5. LLM returns recommendation text + optional structured output
6. Backend formats and returns response to client

---

## 2. Project Phases

### Phase 0 – Foundations & Project Setup

- **Goals**
  - Initialize project structure, tooling, and basic configs.
- **Key Tasks**
  - Choose stack (e.g., Node.js/TypeScript + Express/Fastify, or Python + FastAPI).
  - Set up package manager, linting, formatting, testing (e.g., Jest/Pytest).
  - Create base project layout:
    - `src/api/` – route handlers / controllers
    - `src/services/` – business logic services
    - `src/data/` – dataset access, caching, and data models
    - `src/llm/` – LLM client, prompt templates, and response parsing
    - `src/config/` – configuration loading (env variables, constants)
    - `src/utils/` – helpers, error types, logging
    - `tests/` – unit and integration tests
  - Configure environment variables for:
    - Hugging Face access token
    - LLM provider API key(s)
    - Service port, environment, logging level

### Phase 1 – Data Ingestion & Modeling

- **Goals**
  - Connect to the Hugging Face dataset and define the internal restaurant data model.
- **Key Components**
  - `src/data/hfClient`:
    - Thin client over Hugging Face datasets API.
    - Responsible for authentication and dataset download/streaming.
  - `src/data/models`:
    - Restaurant entity model (id, name, address, locality, city, latitude/longitude if available, cuisines, price range, ratings, votes, etc.).
    - Enumerations / types for cuisine, price band, rating scales.
  - `src/data/loader`:
    - Logic to:
      - Download dataset (initial load) from Hugging Face.
      - Normalize fields into the internal restaurant model.
      - Optionally sample or partition data for development vs production.
  - `src/data/storage`:
    - Abstraction over where data is stored:
      - In-memory cache for local development.
      - Optionally, a lightweight database (e.g., SQLite/Postgres) or persistent cache (e.g., Redis) for production.

### Phase 2 – Preprocessing, Indexing & Filtering

- **Goals**
  - Make dataset queryable efficiently for user preferences (price, place, rating, cuisine).
- **Key Components**
  - `src/data/indexes`:
    - In-memory indexes or DB indices to support queries by:
      - Location (city, locality, or approximate geo).
      - Cuisine(s).
      - Price range.
      - Minimum rating and/or minimum number of votes.
  - `src/services/restaurantQueryService`:
    - Core logic for:
      - Translating user preferences to filter predicates.
      - Retrieving a candidate list of restaurants that match constraints.
      - Sorting by rating, popularity, or distance (if location coordinates exist).
      - Limiting to top N candidates to feed into the LLM.
  - **Configuration**
    - Tunable parameters:
      - Maximum number of candidates before LLM (e.g., 20–50).
      - Default radius/region if location is ambiguous.
      - Fallback rules if no restaurants match strict filters.

### Phase 3 – API Design & Request Handling

- **Goals**
  - Expose a clear API for clients to request recommendations, and standardize how requests are prepared for the Gemini LLM.
- **Key Components**
  - `src/api/routes/recommendations`:
    - Example endpoint: `POST /api/recommendations`
    - Request body schema:
      - `location` / `city` / `area`
      - `price_range` (e.g., low/medium/high or numeric band)
      - `min_rating`
      - `cuisines` (one or multiple)
      - Optional: `max_results`, dietary preferences, ambiance preferences, etc.
    - Response schema:
      - `recommendations`: array of objects with:
        - `name`, `address`, `cuisine`, `price_range`, `rating`, `link`/`source_id`
        - `summary`: natural-language description (from LLM)
      - `explanation`: high-level rationale / summary paragraph from the Gemini LLM.
  - `src/api/middleware`:
    - Validation (using a schema library).
    - Error handling / standardized error responses.
    - Request logging and correlation IDs (for tracing Gemini LLM calls per request).
  - **Configuration for Gemini**
    - The API layer will rely on a **Gemini API key** provided via environment variables (e.g., `GEMINI_API_KEY`).
    - All downstream LLM interactions (Phase 4) will assume Gemini as the primary provider, and the API contract will be designed accordingly (error formats, latency expectations, token limits).

### Phase 4 – LLM Integration & Prompting

- **Goals**
  - Integrate an LLM to generate high-quality, user-centric recommendations based on filtered candidate restaurants.
- **Key Components**
  - `src/llm/client`:
    - Adapter around chosen LLM provider (e.g., OpenAI / Anthropic / Hugging Face Inference).
    - Handles:
      - API keys and model selection.
      - Timeouts and basic retry logic.
      - Cost/usage tracking metadata.
  - `src/llm/prompts`:
    - Prompt templates that:
      - Provide the user’s preferences.
      - Provide a structured list of candidate restaurants (with key fields only).
      - Ask the LLM to:
        - Select the best subset (e.g., 3–5 restaurants).
        - Justify selection in concise, user-friendly language.
        - Optionally return a structured JSON along with natural language.
  - `src/llm/parser`:
    - Logic to parse LLM outputs safely.
    - Validation of structured JSON (if used) against a schema.
    - Fallback to rule-based logic if parsing fails.
  - `src/services/recommendationService`:
    - Orchestrates:
      - Calling `restaurantQueryService` for candidates.
      - Building the LLM prompt.
      - Calling `llm/client` and parsing results.
      - Returning a final standardized response to API layer.

### Phase 5 – UI / Client Integration (Optional)

- **Goals**
  - Provide a simple front-end interface to interact with the service.
- **Key Components**
  - Web client (e.g., React, Next.js, or simple HTML/JS):
    - Form for user to input:
      - Location/place
      - Desired cuisine(s)
      - Budget/price
      - Minimum rating
    - Displays recommendation cards with:
      - Restaurant name, cuisine, rating, price, and LLM-generated description.
  - Client-side service:
    - Handles API calls to `POST /api/recommendations`.
    - Error and loading state handling.

### Phase 6 – Observability, Performance & Reliability

- **Goals**
  - Ensure the system is observable, performs well, and is cost-aware.
- **Key Components**
  - `src/utils/logger`:
    - Structured logging (request IDs, user preferences summary, number of candidates, LLM model, latency).
  - Metrics & monitoring:
    - Latency of:
      - Data query
      - LLM call
      - End-to-end request.
    - LLM usage:
      - Tokens per request.
      - Errors/timeouts.
  - Caching strategies:
    - Cache preprocessed restaurant data.
    - Optional caching of popular recommendation queries (e.g., “best Italian in New York, mid-range”).
  - Reliability:
    - Fallback if LLM fails:
      - Return purely rule-based top N restaurants sorted by rating and popularity.

### Phase 7 – Evaluation, Tuning & Extensions

- **Goals**
  - Improve recommendation quality and prepare for future enhancements.
- **Key Activities**
  - Collect user feedback (thumbs up/down, reasons).
  - A/B test:
    - Different prompt templates.
    - Different ranking heuristics (rating vs rating + votes vs distance).
  - Add more advanced features:
    - Personalized history-based recommendations (if users are authenticated).
    - Support for dietary restrictions or ambiance (romantic, family, business).
    - Multi-language output using LLM.

---

## 3. Non-Functional Requirements

- **Scalability**
  - Support horizontal scaling of API layer.
  - Ensure caching and indexing are in place to avoid querying the full dataset on every request.
- **Security**
  - Store API keys (Hugging Face, LLM provider) securely via environment variables or secrets manager.
  - Implement basic rate limiting to avoid abuse and control costs.
- **Privacy**
  - Avoid storing any sensitive user data (only store anonymous preference logs if needed for analytics).
- **Cost Management**
  - Limit max tokens per LLM call.
  - Consider falling back to heuristic-only responses when budget thresholds are met.

---

## 4. Directory Structure (Proposed)

```text
ARCHITECTURE.md
README.md
package.json / pyproject.toml           # depending on backend stack
src/
  api/
    routes/
      recommendations.ts|py
    middleware/
  services/
    recommendationService.ts|py
    restaurantQueryService.ts|py
  data/
    hfClient.ts|py
    loader.ts|py
    storage.ts|py
    models.ts|py
    indexes.ts|py
  llm/
    client.ts|py
    prompts.ts|py
    parser.ts|py
  config/
    index.ts|py
  utils/
    logger.ts|py
    errors.ts|py
tests/
  api/
  services/
  data/
  llm/
```

This architecture file should guide implementation across phases without constraining specific library choices too tightly. The next step is to pick the backend stack (Node/TypeScript vs Python) and begin implementing Phase 0 and Phase 1 following this structure.

