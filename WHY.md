<!--
Document : WHY.md
Auteur : Bruno DELNOZ
Email : bruno.delnoz@protonmail.com
Version : v1.0.0
Date : 2026-04-20 11:33
-->
# WHY

## Purpose
This repository exists to transform heterogeneous AI conversation exports into analyzable, prompt-driven outputs with minimal operational friction.

## Why this project is useful
- Teams often store historical conversations across multiple AI products.
- Native exports differ in schema and are difficult to compare directly.
- Manual review does not scale for security, moderation, or quality-control use cases.

The tool solves this by normalizing extraction and automating analysis workflows.

## Design choices
### 1) Multi-format ingestion
Support for ChatGPT, LeChat, and Claude prevents lock-in and enables unified processing pipelines.

### 2) Prompt-driven analysis
Separating logic into external prompt templates allows domain-specific analysis (security, child safety, etc.) without code edits.

### 3) Operational modes for real and safe testing
- **Real mode** uses Mistral API for production-grade responses.
- **Simulation mode** validates pipeline behavior offline or before spending tokens.

### 4) Scalable processing
Threaded workers and per-run delay controls balance throughput and API reliability.

### 5) Traceability and reporting
Configurable logs/results directories plus multiple output formats support:
- analyst workflows,
- machine pipelines,
- reporting and archival requirements.

## Typical use cases
- Security and compliance review of AI-assisted engineering discussions.
- Child safety / moderation risk screening.
- Structured thematic extraction from long historical conversations.
- Batch reporting across mixed export sources.

## Non-goals
- This project is not a model training framework.
- It is not a GUI-based annotation suite.
- It does not replace human validation for high-risk decisions.
