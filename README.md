# Delphi

Delphi is an AI-powered student productivity assistant developed by a team at the Claremont Colleges.

## Repository Structure

- frontend/ - Next.js and TypeScript application
- backend/ - Python and FastAPI application
- backend/app/api/ - API endpoints
- backend/app/core/ - Backend configuration
- backend/app/models/ - Database models
- backend/app/schemas/ - Request and response schemas
- backend/app/services/memory/ - Memory retrieval
- backend/app/services/imports/ - Note ingestion
- backend/app/services/recommendations/ - Recommendation logic
- docs/ - Shared technical documentation
- shared/fixtures/ - Shared sample data

## Technology Stack

- Frontend: Next.js and TypeScript
- Backend: Python and FastAPI
- Database: PostgreSQL
- Memory: Python-based retrieval
- Recommendations: Python-based prototype

## Getting Started

Clone the repository and copy the environment template:

    cp .env.example .env

Backend and frontend installation instructions will be added as the respective applications are implemented.

## Development Workflow

See CONTRIBUTING.md.

Each developer works on a separate branch and opens a pull request before merging into main.

## Week 1 Goals

- Runnable backend API
- Basic note and task persistence
- Memory retrieval prototype
- Markdown ingestion prototype
- Recommendation prototype
- Frontend skeleton
- Basic integration smoke test

The full application is not expected to be complete during Week 1.
