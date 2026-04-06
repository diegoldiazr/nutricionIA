# CLAUDE.md

## Project Overview

This project is a **self-hosted AI Nutrition Assistant** designed to help a user lose weight while preserving muscle mass.

The system acts as a **personal AI nutritionist**.

The application runs locally using Docker and uses a **multi-agent architecture**.

The system retrieves all nutrition knowledge from **NotebookLM** and never fabricates nutritional facts.

AI models are accessed through **OpenRouter**.

---

# Core Principles

1. Nutrition advice must NEVER be fabricated.
2. All nutrition knowledge must come from NotebookLM retrieval.
3. Agents must remain modular and independent.
4. The orchestrator coordinates agent communication.
5. SQLite is the persistent database.
6. The system must remain deployable with Docker.

---

# System Architecture

The system uses a **multi-agent architecture**.

Agents:

Knowledge Agent
User Agent
Nutrition Agent
Meal Planner Agent
Recipe Agent
Progress Agent
Recommendation Agent
Memory Agent
Orchestrator Agent

Architecture:

NotebookLM
↓
Knowledge Agent
↓
AI Orchestrator
↓
Specialized Agents
↓
SQLite Database
↓
Backend API
↓
NextJS Frontend

---

# Agent Responsibilities

## Knowledge Agent

Responsible for retrieving nutrition information from NotebookLM.

Functions:

- send queries
- retrieve grounded responses
- return structured knowledge

This agent prevents hallucinations.

---

## User Agent

Manages user data:

- profile
- preferences
- weight history

Stores and retrieves data from SQLite.

---

## Nutrition Agent

Calculates physiological metrics:

- BMR
- TDEE
- calorie targets
- macronutrient targets

---

## Meal Planner Agent

Generates meal suggestions based on:

- remaining calories
- macros
- user preferences

May call the Knowledge Agent when needed.

---

## Recipe Agent

Generates recipes compatible with:

- Airfryer
- Thermomix
- simple home cooking

Recipes must fit calorie and macro targets.

---

## Progress Agent

Analyzes weekly user progress.

Inputs:

- weight change
- calorie intake
- training

Outputs:

- feedback
- adjustment suggestions

---

## Recommendation Agent

Produces high level coaching recommendations.

Example:

- adjust calories
- change protein intake
- suggest meal timing

---

## Memory Agent

Tracks patterns:

- favorite meals
- recurring foods
- hunger patterns

This allows the system to personalize recommendations.

---

## Orchestrator Agent

Central controller.

Responsibilities:

- coordinate agents
- combine results
- generate final output for frontend

---

# Database

SQLite database.

Tables:

users
weight_history
meals
daily_macros
preferences
memory_patterns

Use SQLAlchemy ORM.

---

# Backend

Framework:

FastAPI

API endpoints:

/profile
/log-meal
/daily-summary
/meal-suggestions
/progress-analysis
/settings

---

# AI Integration

AI requests are sent through OpenRouter.

The system must allow model configuration.

Recommended models:

Claude
GPT models

---

# NotebookLM Integration

A service module called:

notebooklm_connector

Responsibilities:

- authenticate via Google OAuth
- select NotebookLM workspace
- send knowledge queries

---

# Docker Deployment

The system must run with:

docker-compose up

Services:

frontend
backend

SQLite data must be persisted via Docker volume.

---

# Coding Guidelines

Follow these principles:

- modular code
- strongly typed where possible
- clear separation of agents
- readable architecture
- maintainable design

---

# Future Extensions

Possible future features:

food photo recognition
voice food logging
automatic grocery list generation
smart recipe generation
integration with fitness apps

---

# Important Rule

Claude must never generate nutritional facts unless they come from NotebookLM retrieval.