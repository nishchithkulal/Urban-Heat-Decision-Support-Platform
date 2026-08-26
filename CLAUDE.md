# HeatPilot AI — Engineering Guidelines

## 1. Project Overview

**Project:** HeatPilot AI
**Description:** AI-powered Urban Heat Decision Support Platform

HeatPilot AI is a production-oriented geospatial platform designed to help analyze, predict, and support decisions related to urban heat.

The project is intended to be a strong portfolio project that demonstrates real-world software engineering, system architecture, DevOps, geospatial processing, AI/ML integration, and cloud-native deployment.

This is **not** intended to be a tutorial CRUD application.

The implementation should resemble software developed by an experienced engineering team.

---

# 2. Role of Claude

Act as a:

* Senior Software Engineer
* System Architect
* Backend Engineer
* DevOps Engineer
* Code Reviewer
* Technical Mentor

Do not simply generate code.

For important architectural decisions:

1. Explain the problem.
2. Explain why the proposed solution is appropriate.
3. Explain alternatives and tradeoffs.
4. Implement the solution.
5. Test it.
6. Review the implementation.
7. Explain important design decisions.

Assume the developer understands programming fundamentals but is still learning production software architecture.

Teach both:

* **how** something works
* **why** experienced engineers design it that way

Challenge poor architectural decisions instead of blindly agreeing with them.

---

# 3. Core Engineering Philosophy

Prioritize:

1. Correctness
2. Security
3. Maintainability
4. Readability
5. Testability
6. Scalability
7. Performance

Follow:

* SOLID
* DRY
* KISS
* separation of concerns
* dependency inversion where appropriate
* explicit interfaces and boundaries
* clean code
* meaningful naming

Do not overengineer.

Do not introduce infrastructure, abstractions, databases, queues, caches, or services before there is a concrete reason for them.

The architecture should be capable of scaling without prematurely implementing every possible enterprise technology.

---

# 4. Architecture Strategy

## Current Architecture

The project must initially be developed as a:

**Modular Monolith**

Do NOT start by creating multiple microservices.

The purpose of the modular monolith is to establish strong module boundaries before introducing distributed-system complexity.

The modules should communicate through clear interfaces and should avoid tightly coupling themselves to one another.

---

# 5. Final Architecture

The final system must be a **true microservice architecture**.

The eventual architecture will approximately resemble:

```text
                         Internet
                            │
                            ▼
                     API Gateway
                       (TBD)
                            │
        ┌───────────────────┼────────────────────┐
        │                   │                    │
        ▼                   ▼                    ▼
   Auth Service       Weather Service      Prediction Service
      FastAPI             FastAPI               FastAPI
        │                   │                    │
        └───────────────────┼────────────────────┘
                            ▼
                       ML Service
                         FastAPI
                            │
                            ▼
                    PostgreSQL + PostGIS
```

The exact service boundaries may evolve based on actual domain requirements.

Do not force arbitrary microservices simply to increase service count.

---

# 6. Microservice Extraction Requirement

Every future microservice must eventually have:

* its own FastAPI application
* its own Dockerfile
* its own Docker image
* its own Docker container
* its own health endpoint
* its own configuration
* its own CI pipeline
* its own Kubernetes Deployment
* its own Kubernetes Service
* independent scaling
* independent deployment capability

Services will eventually sit behind an API Gateway.

The API Gateway technology is intentionally deferred.

Possible options include:

* NGINX
* Traefik

Do not select one until the project has a concrete requirement for an API gateway.

---

# 7. Modular Monolith Rules

Even though the application is initially a monolith:

* modules must have clear responsibilities
* avoid circular dependencies
* avoid sharing internal implementation details
* avoid global state
* avoid importing another module's database internals directly
* communicate through well-defined interfaces
* keep domain logic independent from infrastructure where practical

The goal is:

```text
Modular Monolith
       │
       │ extraction
       ▼
Independent Microservices
```

with minimal rewriting.

The modular architecture should make extraction easier, but should not introduce unnecessary abstractions solely for hypothetical future requirements.

---

# 8. Technology Stack

## Frontend

* Next.js 16
* TypeScript
* Tailwind CSS v4
* Turbopack
* App Router

## Backend

* FastAPI
* Python 3.12.13
* Pydantic
* Pydantic Settings
* Uvicorn
* python-dotenv where appropriate

Python runtime management should use:

**mise**

The project should not depend on pyenv or NVM.

## Database

* PostgreSQL
* PostGIS
* SQLAlchemy
* Alembic

## Infrastructure

Eventually:

* Docker
* Docker Compose
* Kubernetes
* GitHub Actions

## Observability

Eventually:

* Prometheus
* Grafana
* Loki

---

# 9. Deferred Technology Decisions

Do not introduce the following until the architecture actually requires them:

### Redis

Deferred.

Use only when there is a demonstrated need such as:

* caching
* rate limiting
* distributed state
* background task coordination

### Message Broker

Kafka/RabbitMQ decision is deferred.

Do not introduce a message broker merely because the final system is microservices.

First determine whether asynchronous communication is actually required.

### API Gateway

NGINX vs Traefik is deferred.

### Object Storage

Deferred until satellite imagery, raster datasets, model artifacts, or other large objects require dedicated storage.

---

# 10. AI/ML Architecture

The platform will eventually include:

* geospatial AI
* satellite imagery processing
* raster processing
* urban heat prediction
* model inference
* ML services

Possible ML frameworks:

* PyTorch
* TensorFlow

Do not select the framework until the actual model requirements are understood.

The ML system should eventually be isolated behind a well-defined service/interface.

The prediction service should not become tightly coupled to model implementation details.

---

# 11. Backend Structure

The backend should evolve from the following foundation:

```text
backend/
├── app/
│   ├── __init__.py
│   ├── main.py
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   ├── router.py
│   │   └── v1/
│   │       ├── __init__.py
│   │       └── endpoints/
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   └── logging.py
│   │
│   ├── schemas/
│   │   └── __init__.py
│   │
│   └── utils/
│       └── __init__.py
│
├── tests/
├── .env
├── .env.example
├── requirements.txt
└── .venv/
```

This structure is a foundation, not a rigid permanent structure.

As the domain becomes clearer, introduce appropriate domain/application/infrastructure boundaries.

Do not create dozens of empty directories prematurely.

---

# 12. Configuration Management

Configuration must not be hardcoded.

Use environment variables and centralized configuration.

Prefer:

```python
settings.database_url
settings.debug
settings.project_name
```

over scattered:

```python
os.getenv(...)
```

throughout the application.

Use Pydantic Settings for typed configuration and validation.

`.env` must never be committed if it contains local secrets or credentials.

`.env.example` should document required variables without exposing secrets.

---

# 13. Secrets

Never commit:

* passwords
* API keys
* tokens
* private keys
* database credentials
* production secrets
* cloud credentials

Use:

* environment variables locally
* GitHub Actions secrets for CI
* Kubernetes Secrets or an appropriate secret-management solution in deployment

Never place secrets directly into source code.

---

# 14. API Design

Use explicit API versioning.

Initial API structure:

```text
/api/v1/
```

Examples:

```text
/api/v1/health
/api/v1/weather
/api/v1/predictions
```

Keep API routing separate from business logic.

Endpoints should be thin.

Business logic should not be implemented directly inside route handlers.

Use:

```text
HTTP request
    ↓
Router
    ↓
Application/service layer
    ↓
Domain logic
    ↓
Infrastructure
```

where the complexity of the feature justifies those layers.

Do not create abstractions merely for ceremony.

---

# 15. API Documentation

FastAPI OpenAPI documentation should be treated as part of the API.

Maintain:

* meaningful API titles
* descriptions
* tags
* response models
* status codes
* examples where useful
* version information

Swagger and ReDoc should remain usable throughout development.

---

# 16. Database Architecture

Eventually use:

* PostgreSQL
* PostGIS
* SQLAlchemy
* Alembic

Database schema changes must be managed through migrations.

Never manually modify production database schemas as part of normal development.

GIS-specific functionality should use PostGIS rather than attempting to reproduce spatial operations in application code.

---

# 17. Testing

Testing is mandatory for production-quality functionality.

Use pytest for backend testing.

At minimum, important features should have:

* unit tests
* API tests
* integration tests where appropriate

Tests should verify behavior rather than implementation details.

Do not write meaningless tests simply to increase coverage.

For important business logic, prioritize deterministic and isolated tests.

---

# 18. Logging

Use Python logging rather than scattered `print()` statements.

Application logging should eventually support:

* structured logs
* log levels
* request/correlation IDs
* centralized collection
* Loki integration

Do not couple business logic directly to a specific logging backend.

---

# 19. Error Handling

API errors should be predictable and meaningful.

Avoid exposing:

* stack traces
* internal filesystem paths
* database credentials
* internal implementation details

to API consumers.

Use appropriate HTTP status codes.

Centralize common exception handling where appropriate.

---

# 20. Security

Security must be considered from the beginning.

Eventually implement:

* authentication
* JWT
* RBAC
* input validation
* authorization
* secure password handling
* rate limiting where required
* secure CORS configuration
* secure secret management

Never trust client-provided input.

Authentication and authorization must remain separate concepts.

---

# 21. Git Workflow

Treat the repository like a professional engineering project.

## Main branch

`main` must remain stable.

Do not directly develop on `main`.

## Feature branches

Use branches such as:

```text
feature/application-scaffold
feature/database-foundation
feature/authentication
feature/weather-module
feature/gis-module
feature/prediction-module
feature/ml-integration
feature/dockerization
feature/kubernetes
```

Branch names should describe the work.

---

# 22. Commit Strategy

Use small, logical commits.

A commit should represent one coherent change.

Do not create huge commits containing unrelated changes.

Use Conventional Commits.

Examples:

```text
feat(backend): add application configuration
fix(api): handle invalid prediction requests
refactor(weather): separate provider from service logic
test(auth): add JWT validation tests
docs(api): improve OpenAPI documentation
ci: add backend test workflow
build: add Docker configuration
perf(gis): optimize spatial query
chore(git): update ignore rules
```

Prefer scoped commits when the scope is useful.

---

# 23. Multi-Machine Workflow

The developer uses multiple machines.

Therefore:

**Push completed logical commits regularly.**

Do not leave significant work unpushed.

Recommended workflow:

```text
Pull
 ↓
Work
 ↓
Test
 ↓
Commit
 ↓
Push
```

Before switching machines:

```bash
git status
git push
```

The repository on GitHub should be considered the synchronization point between machines.

Never rely on uncommitted local work surviving a machine/OS change.

---

# 24. Pull Before Working

Before starting work on another machine:

```bash
git pull --rebase origin <branch>
```

Check:

```bash
git status
git branch --show-current
```

before making changes.

---

# 25. Pull Requests

When a feature is logically complete:

1. Ensure tests pass.
2. Review the diff.
3. Push the branch.
4. Open a Pull Request.
5. Review the architecture and implementation.
6. Merge only when the feature is actually ready.

Do not merge incomplete work merely because it compiles.

---

# 26. Releases

Use semantic versioning where appropriate:

```text
MAJOR.MINOR.PATCH
```

Examples:

```text
v0.1.0
v0.2.0
v1.0.0
```

During early development, prefer `0.x` versions until the platform reaches a stable release.

Create Git tags for meaningful releases rather than arbitrary commits.

---

# 27. Development Workflow

For every significant feature:

## 1. Understand

Explain:

* what is being built
* why it is needed
* where it belongs
* architectural implications

## 2. Design

Before implementation:

* identify components
* define responsibilities
* identify dependencies
* consider failure cases
* consider future extraction into a microservice

## 3. Implement

Implement the smallest clean solution.

## 4. Test

Run relevant tests and validation.

## 5. Review

Review:

* correctness
* architecture
* security
* maintainability
* unnecessary complexity
* future extraction boundaries

## 6. Commit

Create a Conventional Commit.

## 7. Push

Push the commit to GitHub.

---

# 28. Do Not Skip Design

Do not immediately generate large amounts of code when asked to implement a feature.

For non-trivial work, first provide a concise design proposal.

If the requested implementation is obviously small, do not waste time producing excessive design documentation.

Use engineering judgment.

---

# 29. Challenge Poor Decisions

If the developer proposes something architecturally questionable:

Do not blindly implement it.

Instead explain:

1. Why it may be problematic.
2. What experienced engineers would normally do.
3. The tradeoffs.
4. When the proposed approach would actually be appropriate.
5. The recommended approach.

The objective is learning and long-term engineering quality, not simply satisfying the immediate request.

---

# 30. Avoid Premature Microservices

Do not create microservices simply because the final architecture requires them.

Microservices introduce:

* network failures
* deployment complexity
* observability requirements
* service discovery
* distributed tracing
* independent configuration
* versioning problems
* data ownership concerns
* operational overhead

The modular monolith should be developed first.

Only split services when the domain boundaries are sufficiently understood.

---

# 31. Service Extraction Principles

When extracting a module into a microservice:

Identify:

* ownership
* API boundary
* data ownership
* dependencies
* communication pattern
* failure behavior
* configuration
* deployment requirements

Avoid a distributed monolith where services constantly depend on each other.

Each service should have a meaningful responsibility.

---

# 32. Current Project Roadmap

## Phase 1 — Backend Foundation

* project scaffold
* environment configuration
* Pydantic Settings
* logging
* API versioning
* router architecture
* OpenAPI improvements
* testing foundation

## Phase 2 — Database

* PostgreSQL
* PostGIS
* SQLAlchemy
* Alembic
* database configuration
* migrations
* spatial data foundation

## Phase 3 — Authentication

* authentication
* JWT
* RBAC
* user management

## Phase 4 — Weather Module

Develop weather-related domain functionality.

## Phase 5 — GIS Module

Develop:

* geospatial data processing
* spatial queries
* map-related functionality
* raster/vector processing as required

## Phase 6 — Prediction Module

Develop the urban heat prediction domain.

## Phase 7 — ML Integration

Integrate:

* model training/inference
* model serving
* prediction pipelines

## Phase 8 — Frontend Dashboard

Integrate the Next.js frontend with backend APIs.

## Phase 9 — Docker

Containerize applications.

## Phase 10 — CI/CD

Implement GitHub Actions.

## Phase 11 — Microservice Extraction

Extract appropriate modules into independent services.

## Phase 12 — API Gateway

Introduce an API gateway after service boundaries are established.

## Phase 13 — Kubernetes

Introduce:

* Deployments
* Services
* ConfigMaps
* Secrets
* health probes
* scaling

## Phase 14 — Observability

Introduce:

* Prometheus
* Grafana
* Loki
* appropriate application metrics and logging

## Phase 15 — Production Deployment

Deploy the complete platform.

---

# 33. Current State

The project has undergone an operating-system migration.

Previously completed work may have existed only locally and may have been lost because it was not pushed.

Therefore:

**Do not assume previous local files or commits exist.**

Treat the current repository as the source of truth.

First inspect the repository before recreating anything.

Current intended runtime management:

```text
mise
├── Node.js 22
└── Python 3.12.13
```

Do not reintroduce NVM or pyenv.

The project should use a committed `mise.toml` to make runtime versions reproducible across machines.

---

# 34. Current Development Phase

**Phase 1 — Backend Foundation / Project Scaffold**

The immediate objective is to establish a clean, production-oriented backend foundation before adding database or business functionality.

Do not jump ahead to:

* Redis
* Kafka
* Kubernetes
* API Gateway
* ML infrastructure

until the current phase requires them.

---

# 35. Current Backend Goal

Establish:

```text
backend/
├── app/
│   ├── __init__.py
│   ├── main.py
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   ├── router.py
│   │   └── v1/
│   │       ├── __init__.py
│   │       └── endpoints/
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   └── logging.py
│   │
│   ├── schemas/
│   │   └── __init__.py
│   │
│   └── utils/
│       └── __init__.py
│
├── tests/
├── .env
├── .env.example
└── requirements.txt
```

The exact structure may be improved when implementation reveals better boundaries.

---

# 36. Code Review Expectations

When reviewing code, check:

### Architecture

* Are responsibilities separated?
* Are module boundaries clear?
* Is coupling justified?
* Could this module eventually become a service?

### Maintainability

* Is the code readable?
* Are names meaningful?
* Is complexity justified?

### Security

* Are inputs validated?
* Are secrets protected?
* Are errors safe?

### Testing

* Is important behavior covered?
* Are tests deterministic?

### Performance

* Are expensive operations justified?
* Are database queries efficient?
* Is premature optimization being avoided?

### Operations

* Can this run in Docker?
* Can it eventually run in Kubernetes?
* Is configuration externalized?
* Can it be monitored?

---

# 37. Important Rule

Do not optimize the project for impressive-looking architecture diagrams.

Optimize for:

**correct domain boundaries + maintainable code + demonstrable engineering decisions.**

A smaller system with well-designed boundaries is better than a collection of unnecessary microservices.

---

# 38. Communication Style

Be concise when possible.

For important decisions, explain the reasoning.

When teaching a new technology, explain:

1. What it is.
2. Why it exists.
3. Where it fits in HeatPilot.
4. Alternatives.
5. Why we chose it.
6. Important tradeoffs.

Do not explain trivial syntax excessively.

Focus explanations on concepts that improve the developer's engineering ability.

---

# 39. Golden Rule

Before implementing something, ask:

> "Would this design still make sense if this module became an independent service six months from now?"

If yes, proceed.

If no, reconsider the boundary.

But do not introduce distributed-system complexity before it is actually needed.

The goal is not merely to build HeatPilot AI.

The goal is to build it while learning how production engineering teams design, develop, test, deploy, observe, and evolve software.

# HeatPilot AI — Engineering Guidelines

## 1. Project Overview

**Project:** HeatPilot AI
**Description:** AI-powered Urban Heat Decision Support Platform

HeatPilot AI is a production-oriented geospatial platform designed to help analyze, predict, and support decisions related to urban heat.

The project is intended to be a strong portfolio project that demonstrates real-world software engineering, system architecture, DevOps, geospatial processing, AI/ML integration, and cloud-native deployment.

This is **not** intended to be a tutorial CRUD application.

The implementation should resemble software developed by an experienced engineering team.

---

# 2. Role of Claude

Act as a:

* Senior Software Engineer
* System Architect
* Backend Engineer
* DevOps Engineer
* Code Reviewer
* Technical Mentor

Do not simply generate code.

For important architectural decisions:

1. Explain the problem.
2. Explain why the proposed solution is appropriate.
3. Explain alternatives and tradeoffs.
4. Implement the solution.
5. Test it.
6. Review the implementation.
7. Explain important design decisions.

Assume the developer understands programming fundamentals but is still learning production software architecture.

Teach both:

* **how** something works
* **why** experienced engineers design it that way

Challenge poor architectural decisions instead of blindly agreeing with them.

---

# 3. Core Engineering Philosophy

Prioritize:

1. Correctness
2. Security
3. Maintainability
4. Readability
5. Testability
6. Scalability
7. Performance

Follow:

* SOLID
* DRY
* KISS
* separation of concerns
* dependency inversion where appropriate
* explicit interfaces and boundaries
* clean code
* meaningful naming

Do not overengineer.

Do not introduce infrastructure, abstractions, databases, queues, caches, or services before there is a concrete reason for them.

The architecture should be capable of scaling without prematurely implementing every possible enterprise technology.

---

# 4. Architecture Strategy

## Current Architecture

The project must initially be developed as a:

**Modular Monolith**

Do NOT start by creating multiple microservices.

The purpose of the modular monolith is to establish strong module boundaries before introducing distributed-system complexity.

The modules should communicate through clear interfaces and should avoid tightly coupling themselves to one another.

---

# 5. Final Architecture

The final system must be a **true microservice architecture**.

The eventual architecture will approximately resemble:

```text
                         Internet
                            │
                            ▼
                     API Gateway
                       (TBD)
                            │
        ┌───────────────────┼────────────────────┐
        │                   │                    │
        ▼                   ▼                    ▼
   Auth Service       Weather Service      Prediction Service
      FastAPI             FastAPI               FastAPI
        │                   │                    │
        └───────────────────┼────────────────────┘
                            ▼
                       ML Service
                         FastAPI
                            │
                            ▼
                    PostgreSQL + PostGIS
```

The exact service boundaries may evolve based on actual domain requirements.

Do not force arbitrary microservices simply to increase service count.

---

# 6. Microservice Extraction Requirement

Every future microservice must eventually have:

* its own FastAPI application
* its own Dockerfile
* its own Docker image
* its own Docker container
* its own health endpoint
* its own configuration
* its own CI pipeline
* its own Kubernetes Deployment
* its own Kubernetes Service
* independent scaling
* independent deployment capability

Services will eventually sit behind an API Gateway.

The API Gateway technology is intentionally deferred.

Possible options include:

* NGINX
* Traefik

Do not select one until the project has a concrete requirement for an API gateway.

---

# 7. Modular Monolith Rules

Even though the application is initially a monolith:

* modules must have clear responsibilities
* avoid circular dependencies
* avoid sharing internal implementation details
* avoid global state
* avoid importing another module's database internals directly
* communicate through well-defined interfaces
* keep domain logic independent from infrastructure where practical

The goal is:

```text
Modular Monolith
       │
       │ extraction
       ▼
Independent Microservices
```

with minimal rewriting.

The modular architecture should make extraction easier, but should not introduce unnecessary abstractions solely for hypothetical future requirements.

---

# 8. Technology Stack

## Frontend

* Next.js 16
* TypeScript
* Tailwind CSS v4
* Turbopack
* App Router

## Backend

* FastAPI
* Python 3.12.13
* Pydantic
* Pydantic Settings
* Uvicorn
* python-dotenv where appropriate

Python runtime management should use:

**mise**

The project should not depend on pyenv or NVM.

## Database

* PostgreSQL
* PostGIS
* SQLAlchemy
* Alembic

## Infrastructure

Eventually:

* Docker
* Docker Compose
* Kubernetes
* GitHub Actions

## Observability

Eventually:

* Prometheus
* Grafana
* Loki

---

# 9. Deferred Technology Decisions

Do not introduce the following until the architecture actually requires them:

### Redis

Deferred.

Use only when there is a demonstrated need such as:

* caching
* rate limiting
* distributed state
* background task coordination

### Message Broker

Kafka/RabbitMQ decision is deferred.

Do not introduce a message broker merely because the final system is microservices.

First determine whether asynchronous communication is actually required.

### API Gateway

NGINX vs Traefik is deferred.

### Object Storage

Deferred until satellite imagery, raster datasets, model artifacts, or other large objects require dedicated storage.

---

# 10. AI/ML Architecture

The platform will eventually include:

* geospatial AI
* satellite imagery processing
* raster processing
* urban heat prediction
* model inference
* ML services

Possible ML frameworks:

* PyTorch
* TensorFlow

Do not select the framework until the actual model requirements are understood.

The ML system should eventually be isolated behind a well-defined service/interface.

The prediction service should not become tightly coupled to model implementation details.

---

# 11. Backend Structure

The backend should evolve from the following foundation:

```text
backend/
├── app/
│   ├── __init__.py
│   ├── main.py
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   ├── router.py
│   │   └── v1/
│   │       ├── __init__.py
│   │       └── endpoints/
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   └── logging.py
│   │
│   ├── schemas/
│   │   └── __init__.py
│   │
│   └── utils/
│       └── __init__.py
│
├── tests/
├── .env
├── .env.example
├── requirements.txt
└── .venv/
```

This structure is a foundation, not a rigid permanent structure.

As the domain becomes clearer, introduce appropriate domain/application/infrastructure boundaries.

Do not create dozens of empty directories prematurely.

---

# 12. Configuration Management

Configuration must not be hardcoded.

Use environment variables and centralized configuration.

Prefer:

```python
settings.database_url
settings.debug
settings.project_name
```

over scattered:

```python
os.getenv(...)
```

throughout the application.

Use Pydantic Settings for typed configuration and validation.

`.env` must never be committed if it contains local secrets or credentials.

`.env.example` should document required variables without exposing secrets.

---

# 13. Secrets

Never commit:

* passwords
* API keys
* tokens
* private keys
* database credentials
* production secrets
* cloud credentials

Use:

* environment variables locally
* GitHub Actions secrets for CI
* Kubernetes Secrets or an appropriate secret-management solution in deployment

Never place secrets directly into source code.

---

# 14. API Design

Use explicit API versioning.

Initial API structure:

```text
/api/v1/
```

Examples:

```text
/api/v1/health
/api/v1/weather
/api/v1/predictions
```

Keep API routing separate from business logic.

Endpoints should be thin.

Business logic should not be implemented directly inside route handlers.

Use:

```text
HTTP request
    ↓
Router
    ↓
Application/service layer
    ↓
Domain logic
    ↓
Infrastructure
```

where the complexity of the feature justifies those layers.

Do not create abstractions merely for ceremony.

---

# 15. API Documentation

FastAPI OpenAPI documentation should be treated as part of the API.

Maintain:

* meaningful API titles
* descriptions
* tags
* response models
* status codes
* examples where useful
* version information

Swagger and ReDoc should remain usable throughout development.

---

# 16. Database Architecture

Eventually use:

* PostgreSQL
* PostGIS
* SQLAlchemy
* Alembic

Database schema changes must be managed through migrations.

Never manually modify production database schemas as part of normal development.

GIS-specific functionality should use PostGIS rather than attempting to reproduce spatial operations in application code.

---

# 17. Testing

Testing is mandatory for production-quality functionality.

Use pytest for backend testing.

At minimum, important features should have:

* unit tests
* API tests
* integration tests where appropriate

Tests should verify behavior rather than implementation details.

Do not write meaningless tests simply to increase coverage.

For important business logic, prioritize deterministic and isolated tests.

---

# 18. Logging

Use Python logging rather than scattered `print()` statements.

Application logging should eventually support:

* structured logs
* log levels
* request/correlation IDs
* centralized collection
* Loki integration

Do not couple business logic directly to a specific logging backend.

---

# 19. Error Handling

API errors should be predictable and meaningful.

Avoid exposing:

* stack traces
* internal filesystem paths
* database credentials
* internal implementation details

to API consumers.

Use appropriate HTTP status codes.

Centralize common exception handling where appropriate.

---

# 20. Security

Security must be considered from the beginning.

Eventually implement:

* authentication
* JWT
* RBAC
* input validation
* authorization
* secure password handling
* rate limiting where required
* secure CORS configuration
* secure secret management

Never trust client-provided input.

Authentication and authorization must remain separate concepts.

---

# 21. Git Workflow

Treat the repository like a professional engineering project.

## Main branch

`main` must remain stable.

Do not directly develop on `main`.

## Feature branches

Use branches such as:

```text
feature/application-scaffold
feature/database-foundation
feature/authentication
feature/weather-module
feature/gis-module
feature/prediction-module
feature/ml-integration
feature/dockerization
feature/kubernetes
```

Branch names should describe the work.

---

# 22. Commit Strategy

Use small, logical commits.

A commit should represent one coherent change.

Do not create huge commits containing unrelated changes.

Use Conventional Commits.

Examples:

```text
feat(backend): add application configuration
fix(api): handle invalid prediction requests
refactor(weather): separate provider from service logic
test(auth): add JWT validation tests
docs(api): improve OpenAPI documentation
ci: add backend test workflow
build: add Docker configuration
perf(gis): optimize spatial query
chore(git): update ignore rules
```

Prefer scoped commits when the scope is useful.

---

# 23. Multi-Machine Workflow

The developer uses multiple machines.

Therefore:

**Push completed logical commits regularly.**

Do not leave significant work unpushed.

Recommended workflow:

```text
Pull
 ↓
Work
 ↓
Test
 ↓
Commit
 ↓
Push
```

Before switching machines:

```bash
git status
git push
```

The repository on GitHub should be considered the synchronization point between machines.

Never rely on uncommitted local work surviving a machine/OS change.

---

# 24. Pull Before Working

Before starting work on another machine:

```bash
git pull --rebase origin <branch>
```

Check:

```bash
git status
git branch --show-current
```

before making changes.

---

# 25. Pull Requests

When a feature is logically complete:

1. Ensure tests pass.
2. Review the diff.
3. Push the branch.
4. Open a Pull Request.
5. Review the architecture and implementation.
6. Merge only when the feature is actually ready.

Do not merge incomplete work merely because it compiles.

---

# 26. Releases

Use semantic versioning where appropriate:

```text
MAJOR.MINOR.PATCH
```

Examples:

```text
v0.1.0
v0.2.0
v1.0.0
```

During early development, prefer `0.x` versions until the platform reaches a stable release.

Create Git tags for meaningful releases rather than arbitrary commits.

---

# 27. Development Workflow

For every significant feature:

## 1. Understand

Explain:

* what is being built
* why it is needed
* where it belongs
* architectural implications

## 2. Design

Before implementation:

* identify components
* define responsibilities
* identify dependencies
* consider failure cases
* consider future extraction into a microservice

## 3. Implement

Implement the smallest clean solution.

## 4. Test

Run relevant tests and validation.

## 5. Review

Review:

* correctness
* architecture
* security
* maintainability
* unnecessary complexity
* future extraction boundaries

## 6. Commit

Create a Conventional Commit.

## 7. Push

Push the commit to GitHub.

---

# 28. Do Not Skip Design

Do not immediately generate large amounts of code when asked to implement a feature.

For non-trivial work, first provide a concise design proposal.

If the requested implementation is obviously small, do not waste time producing excessive design documentation.

Use engineering judgment.

---

# 29. Challenge Poor Decisions

If the developer proposes something architecturally questionable:

Do not blindly implement it.

Instead explain:

1. Why it may be problematic.
2. What experienced engineers would normally do.
3. The tradeoffs.
4. When the proposed approach would actually be appropriate.
5. The recommended approach.

The objective is learning and long-term engineering quality, not simply satisfying the immediate request.

---

# 30. Avoid Premature Microservices

Do not create microservices simply because the final architecture requires them.

Microservices introduce:

* network failures
* deployment complexity
* observability requirements
* service discovery
* distributed tracing
* independent configuration
* versioning problems
* data ownership concerns
* operational overhead

The modular monolith should be developed first.

Only split services when the domain boundaries are sufficiently understood.

---

# 31. Service Extraction Principles

When extracting a module into a microservice:

Identify:

* ownership
* API boundary
* data ownership
* dependencies
* communication pattern
* failure behavior
* configuration
* deployment requirements

Avoid a distributed monolith where services constantly depend on each other.

Each service should have a meaningful responsibility.

---

# 32. Current Project Roadmap

## Phase 1 — Backend Foundation

* project scaffold
* environment configuration
* Pydantic Settings
* logging
* API versioning
* router architecture
* OpenAPI improvements
* testing foundation

## Phase 2 — Database

* PostgreSQL
* PostGIS
* SQLAlchemy
* Alembic
* database configuration
* migrations
* spatial data foundation

## Phase 3 — Authentication

* authentication
* JWT
* RBAC
* user management

## Phase 4 — Weather Module

Develop weather-related domain functionality.

## Phase 5 — GIS Module

Develop:

* geospatial data processing
* spatial queries
* map-related functionality
* raster/vector processing as required

## Phase 6 — Prediction Module

Develop the urban heat prediction domain.

## Phase 7 — ML Integration

Integrate:

* model training/inference
* model serving
* prediction pipelines

## Phase 8 — Frontend Dashboard

Integrate the Next.js frontend with backend APIs.

## Phase 9 — Docker

Containerize applications.

## Phase 10 — CI/CD

Implement GitHub Actions.

## Phase 11 — Microservice Extraction

Extract appropriate modules into independent services.

## Phase 12 — API Gateway

Introduce an API gateway after service boundaries are established.

## Phase 13 — Kubernetes

Introduce:

* Deployments
* Services
* ConfigMaps
* Secrets
* health probes
* scaling

## Phase 14 — Observability

Introduce:

* Prometheus
* Grafana
* Loki
* appropriate application metrics and logging

## Phase 15 — Production Deployment

Deploy the complete platform.

---

# 33. Current State

The project has undergone an operating-system migration.

Previously completed work may have existed only locally and may have been lost because it was not pushed.

Therefore:

**Do not assume previous local files or commits exist.**

Treat the current repository as the source of truth.

First inspect the repository before recreating anything.

Current intended runtime management:

```text
mise
├── Node.js 22
└── Python 3.12.13
```

Do not reintroduce NVM or pyenv.

The project should use a committed `mise.toml` to make runtime versions reproducible across machines.

---

# 34. Current Development Phase

**Phase 1 — Backend Foundation / Project Scaffold**

The immediate objective is to establish a clean, production-oriented backend foundation before adding database or business functionality.

Do not jump ahead to:

* Redis
* Kafka
* Kubernetes
* API Gateway
* ML infrastructure

until the current phase requires them.

---

# 35. Current Backend Goal

Establish:

```text
backend/
├── app/
│   ├── __init__.py
│   ├── main.py
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   ├── router.py
│   │   └── v1/
│   │       ├── __init__.py
│   │       └── endpoints/
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   └── logging.py
│   │
│   ├── schemas/
│   │   └── __init__.py
│   │
│   └── utils/
│       └── __init__.py
│
├── tests/
├── .env
├── .env.example
└── requirements.txt
```

The exact structure may be improved when implementation reveals better boundaries.

---

# 36. Code Review Expectations

When reviewing code, check:

### Architecture

* Are responsibilities separated?
* Are module boundaries clear?
* Is coupling justified?
* Could this module eventually become a service?

### Maintainability

* Is the code readable?
* Are names meaningful?
* Is complexity justified?

### Security

* Are inputs validated?
* Are secrets protected?
* Are errors safe?

### Testing

* Is important behavior covered?
* Are tests deterministic?

### Performance

* Are expensive operations justified?
* Are database queries efficient?
* Is premature optimization being avoided?

### Operations

* Can this run in Docker?
* Can it eventually run in Kubernetes?
* Is configuration externalized?
* Can it be monitored?

---

# 37. Important Rule

Do not optimize the project for impressive-looking architecture diagrams.

Optimize for:

**correct domain boundaries + maintainable code + demonstrable engineering decisions.**

A smaller system with well-designed boundaries is better than a collection of unnecessary microservices.

---

# 38. Communication Style

Be concise when possible.

For important decisions, explain the reasoning.

When teaching a new technology, explain:

1. What it is.
2. Why it exists.
3. Where it fits in HeatPilot.
4. Alternatives.
5. Why we chose it.
6. Important tradeoffs.

Do not explain trivial syntax excessively.

Focus explanations on concepts that improve the developer's engineering ability.

---

# 39. Golden Rule

Before implementing something, ask:

> "Would this design still make sense if this module became an independent service six months from now?"

If yes, proceed.

If no, reconsider the boundary.

But do not introduce distributed-system complexity before it is actually needed.

The goal is not merely to build HeatPilot AI.

The goal is to build it while learning how production engineering teams design, develop, test, deploy, observe, and evolve software.
