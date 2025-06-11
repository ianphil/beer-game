# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Beer Game simulation - an implementation of the Production-Distribution Game designed to demonstrate system dynamics principles. The beer game illustrates how "structure produces behavior" by simulating a supply chain with four positions: retailer, wholesaler, distributor, and factory.

## Setup Commands

```bash
# Install dependencies
uv sync

# Run the main application
uv run src/main.py
```

## Architecture

The project is currently in early development with a minimal Python structure:

- `src/main.py` - Entry point with basic "Hello World" functionality
- `ai_docs/beer-game-instructions.md` - Complete game rules and instructions from the System Dynamics Society
- `pyproject.toml` - Python project configuration using UV package manager

## Game Context

The beer game simulates a 4-tier supply chain where:
- Each position maintains inventory and receives/ships orders
- Players aim to minimize costs ($0.50/case/week inventory + $1.00/case/week backlog)
- Communication between positions is prohibited (mimicking real supply chains)
- Customer demand follows a simple step pattern (4 cases/week then 8 cases/week)
- The game demonstrates how internal system structure generates oscillations, not external events

Refer to `ai_docs/beer-game-instructions.md` for complete game mechanics, rules, and educational objectives.