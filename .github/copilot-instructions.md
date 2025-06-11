# GitHub Copilot Instructions

This repository contains a Beer Game simulation - an implementation of the Production-Distribution Game designed to demonstrate system dynamics principles.

## Project Context

The beer game illustrates how "structure produces behavior" by simulating a supply chain with four positions: retailer, wholesaler, distributor, and factory. The game demonstrates how internal system structure generates oscillations, not external events.

### Key Game Mechanics
- 4-tier supply chain simulation (retailer → wholesaler → distributor → factory)
- Each position maintains inventory and processes orders
- Cost minimization objective: $0.50/case/week inventory + $1.00/case/week backlog
- No communication between positions (realistic supply chain constraint)
- Customer demand pattern: 4 cases/week then step to 8 cases/week
- Shipping and production delays create system dynamics

## Development Setup

```bash
# Install dependencies
uv sync

# Run the application
uv run src/main.py
```

## Current Architecture

- `src/main.py` - Application entry point
- `ai_docs/beer-game-instructions.md` - Complete game rules and educational materials
- `pyproject.toml` - Python project configuration using UV package manager

## Development Guidelines

When contributing code:
- Follow the system dynamics principles embodied in the game design
- Maintain the educational objectives of demonstrating how structure produces behavior
- Implement realistic supply chain constraints (delays, limited communication)
- Focus on the four key positions: retailer, wholesaler, distributor, factory
- Preserve the cost structure that drives decision-making

The game's educational value comes from players experiencing how reasonable individual decisions can create system-wide oscillations and inefficiencies.