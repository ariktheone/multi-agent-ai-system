# Multi-Agent AI System (Google ADK Assignment) — Documentation

---

## Table of Contents

1. [Overview](#overview)
2. [Repository](#repository)
3. [Architecture & Flow](#architecture--flow)
4. [Agent Types](#agent-types)
5. [Data Routing & Enrichment](#data-routing--enrichment)
6. [Iterative Refinement](#iterative-refinement)
7. [Supported APIs & Integrations](#supported-apis--integrations)
8. [Example Agent Chain](#example-agent-chain)
9. [Directory Structure](#directory-structure)
10. [Setup & Running](#setup--running)
11. [How It Works](#how-it-works)
12. [Evaluation & Testing](#evaluation--testing)
13. [Code Quality & Best Practices](#code-quality--best-practices)
14. [For Developers](#for-developers)
15. [Deliverables](#deliverables)
16. [License](#license)

---

## Overview

This project implements a **modular, production-grade multi-agent AI system** using Google ADK principles. The system takes a user-defined research goal, plans a sequence of agent actions, and routes data between agents—each enriching the output of the previous—until the goal is achieved. If the goal is not satisfied, the system iteratively refines the agent chain and re-executes, ensuring robust, actionable results.

**Example Use Case:**  
“Find the next SpaceX launch, check weather at that location, then summarize if it may be delayed.”

---

## Repository

**GitHub:** [https://github.com/ariktheone/multi-agent-ai-system.git](https://github.com/ariktheone/multi-agent-ai-system.git)

---

## Architecture & Flow

### 1. Planner & Agent Chaining

- **PlannerAgent** analyzes the user goal and selects the optimal sequence of agents (the "agent chain") using entity extraction and goal parsing.
- Each agent receives the current context, processes it, and passes enriched results to the next agent.
- The chain is **iteratively refined** if the goal is not met (see `execute_chain` in `main.py`).
- All agent actions, context changes, and errors are logged for transparency and debugging.

---

## Agent Types

- **PlannerAgent:** Determines agent order and adapts the chain if the goal is not satisfied.
- **Enrichment Agents:** Each agent (e.g., WeatherAgent, SpaceXAgent, NewsAgent, SentimentAgent, AirQualityAgent, FinanceAgent, etc.) fetches or analyzes data, depending on the output of previous agents.
- **SummarizerAgent:** Synthesizes all findings into a human-readable, executive summary and detailed report.
- **Specialized Agents:** Additional agents (e.g., FactCheckAgent, BooksAgent, COVIDAgent, PollutionAgent, etc.) can be included based on the research goal.

---

## Data Routing & Enrichment

- Agents do not work in isolation: each depends on the previous agent’s output.
- The `AgentContext` object is passed and enriched at each step, accumulating all intermediate and final results.
- Data enrichment and agent trajectory are tracked and logged for every run.

---

## Iterative Refinement

- If the summary is missing, incomplete, or the goal is not satisfied, the planner refines the agent chain and the system re-executes, up to a maximum number of iterations.
- The planner’s routing logic and all changes to the agent chain are displayed and logged for evaluation.

---

## Supported APIs & Integrations

- **OpenWeatherMap:** Weather and environmental data.
- **SpaceX API:** Next launch details and launchpad location.
- **NewsAPI:** Latest news relevant to the goal.
- **CoinGecko:** Cryptocurrency and financial data.
- **Cohere:** Advanced summarization and NLP (if API key provided).
- **Other APIs:** Google Books, Alpha Vantage, COVID-19, and more (see `agents/` for full list).

All API keys are managed via a `.env` file (see `.env.example`).  
**You must provide your own API keys for full functionality.**

---

## Example Agent Chain

For the goal:  
*"Find the next SpaceX launch, check weather at that location, then summarize if it may be delayed."*

The system will automatically chain:
```
SpaceXAgent → WeatherAgent → NewsAgent → SentimentAgent → SummarizerAgent
```
Each agent uses the previous agent's output (e.g., WeatherAgent uses the launch location from SpaceXAgent).

---

## Directory Structure

```
multi-agent-ai-system/
│
├── agents/           # All agent implementations (planner, enrichment, summarizer)
├── utils/            # Utilities (context, entity extraction, etc.)
├── configs/          # Agent and API configuration files
├── evals/            # Evaluation scripts and tests
├── reports/          # Generated reports (auto-saved)
├── main.py           # Main orchestration logic
├── requirements.txt  # Python dependencies
├── .env.example      # Example API key config
└── README.md         # This file
```

---

## Setup & Running

### 1. Clone the repository
```bash
git clone https://github.com/ariktheone/multi-agent-ai-system.git
cd multi-agent-ai-system
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure API keys
- Copy `.env.example` to `.env`:
  ```bash
  cp .env.example .env
  ```
- Fill in your API keys for all required services (OpenWeatherMap, NewsAPI, Cohere, etc.).

### 4. (Optional) Configure agent settings
- Edit `configs/agents.json` to adjust agent parameters, endpoints, or enable/disable agents.

### 5. Run the platform
```bash
python main.py
```
- Enter your research goal when prompted.
- The system will display the agent workflow, execute the chain, and print/save a detailed report.

---

## How It Works

1. **User provides a research goal** (e.g., "Comprehensive analysis of Tesla's financial performance, market sentiment, and recent news impact on stock valuation").
2. **PlannerAgent** selects and orders the most relevant agents for the goal.
3. **Agents** run in sequence, each enriching the context with new data or analysis.
4. **SummarizerAgent** synthesizes all findings into a multi-section report.
5. **Evaluation logic** checks if the goal is satisfied; if not, the planner refines the chain and the process repeats.
6. **Report** is printed and saved to `reports/` with performance metrics and data quality assessment.

---

## Evaluation & Testing

- **Unit and integration tests** are in [`evals/`](evals/).
- Example: [`test_eval.py`](evals/test_eval.py) checks if the summary is generated and if the agent trajectory is as expected.
- Evaluation covers:
  - **Goal satisfaction:** Is the summary present and sufficiently detailed?
  - **Agent trajectory:** Which agents ran, in what order, and what data did they add?
  - **Planner routing:** Did the planner adapt the chain if the goal was not met?
  - **Iterative refinement:** Was the chain refined and re-executed as needed?
- **Trajectory and enrichment logs** are available for every run.

---

## Code Quality & Best Practices

- **Modular agent design:** All agents inherit from `BaseAgent` for consistency and extensibility.
- **Type hints and docstrings** throughout the codebase.
- **Structured logging:** All agent actions, errors, and planner decisions are logged.
- **Linting/formatting:** Use `black` and `flake8` for code quality.
- **Documentation:** Each agent and utility is documented in its source file.
- **Separation of concerns:** Planning, agent execution, evaluation, and reporting are modularized.

---

## For Developers

- See [`main.py`](main.py) for orchestration logic and agent chaining.
- See [`agents/`](agents/) for all agent implementations (planner, enrichment, summarizer, etc.).
- See [`requirements.txt`](requirements.txt) for dependencies.
- See [`evals/`](evals/) for test scripts and evaluation logic.
- See [`utils/`](utils/) for context management and entity extraction.
- See [`configs/`](configs/) for agent and API configuration.

---

## Deliverables

- **Code:** Modular agents (planner + enrichment agents), main orchestration, and utilities.
- **Docs:** This documentation (architecture, flow, agent logic, APIs, setup, evaluation).
- **Evals:** Test scripts for goal satisfaction and agent trajectory.
- **Evaluation:** Demonstrates agent chaining, data enrichment, planner routing, and iterative refinement.
- **Code quality:** Modular, type-annotated, logged, and well-documented.

---

## License

Internal use only. For demo and research purposes.

---