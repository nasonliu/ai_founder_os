# Contributing to AI Founder OS

Welcome! This project aims to build an AI-native operating system for founders.

## Development Philosophy

1. **Artifact First** - Every task must produce verifiable output
2. **Test Driven** - All new features require tests
3. **Human in the Loop** - Critical decisions require human approval
4. **Incremental** - Small steps, continuous validation

## Getting Started

### Prerequisites
- Python 3.11+
- Git

### Setup

```bash
# Clone
git clone https://github.com/nasonliu/ai_founder_os.git
cd ai_founder_os

# Install dependencies
pip install -r requirements.txt

# Run tests
pytest
```

### Code Style

- Follow PEP 8
- Use type hints
- Add docstrings to public APIs
- Run linting before commit:

```bash
ruff check src/
black src/
mypy src/
```

## Project Structure

```
ai_founder_os/
├── src/
│   ├── planner/      # Task orchestration
│   ├── workers/      # Worker implementations
│   ├── policy/       # Policy engine
│   ├── connections/  # External integrations
│   ├── experience/   # Knowledge system
│   ├── dashboard/    # Dashboard API
│   └── api/          # FastAPI server
├── tests/            # Test suite
├── docs/             # Documentation
└── prompts/          # Agent prompts
```

## Submitting Changes

1. Fork the repo
2. Create a feature branch
3. Add tests for new features
4. Ensure all tests pass
5. Update documentation
6. Submit a Pull Request

## Questions?

Open an issue for bugs or feature requests.
