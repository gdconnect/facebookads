# Facebook Ads Management System

A collection of constitutional single-file Python agents for Facebook Ads management, each following the Schema-First Empire Constitution principles.

## Repository Structure

```
agents/                                    # All agents organized in dedicated folders
├── brand_identity_generator/              # Brand identity enhancement agent
│   ├── brand_identity_generator.py        # Main program
│   ├── README.md                          # Agent documentation
│   ├── schemas/                           # Input/output schemas
│   ├── tests/                             # Agent-specific tests
│   └── examples/                          # Usage examples
├── customer_journey_mapper/               # Customer journey mapping agent
│   ├── customer_journey_mapper.py         # Main program
│   ├── README.md                          # Agent documentation
│   ├── schemas/                           # Input/output schemas
│   ├── tests/                             # Agent-specific tests
│   └── examples/                          # Usage examples
├── constitutional_compliance_validator/   # Constitutional compliance validator
│   ├── constitutional_compliance_validator.py  # Main program
│   ├── README.md                          # Agent documentation
│   ├── schemas/                           # Input/output schemas
│   └── tests/                             # Agent-specific tests
└── _shared/                               # Shared components
    ├── schemas/                           # Shared JSON schemas
    ├── docs/                              # Shared documentation
    └── utils/                             # Shared utilities

specs/                                     # Feature specifications
tests/                                     # Shared integration tests
validation-tests/                          # System validation scripts
.specify/                                  # Development tools and constitution
```

## Available Agents

### 1. Brand Identity Generator
AI-powered brand identity enhancement with automatic font selection and color palette generation.

**Usage:**
```bash
python agents/brand_identity_generator/brand_identity_generator.py brand.md --enhance
```

**Features:**
- Color palette enhancement
- Google Fonts integration
- Typography hierarchy generation
- Brand gap analysis

**Documentation:** [agents/brand_identity_generator/README.md](agents/brand_identity_generator/README.md)

### 2. Customer Journey Mapper
Generate comprehensive customer journey maps for niche markets based on market specifications.

**Usage:**
```bash
python agents/customer_journey_mapper/customer_journey_mapper.py \
  --market-description "Eco-conscious millennials" \
  --industry ecommerce
```

**Features:**
- Market-driven journey generation
- Multiple business model support
- Schema-validated output
- Decision table logic

**Documentation:** [agents/customer_journey_mapper/README.md](agents/customer_journey_mapper/README.md)

### 3. Constitutional Compliance Validator
Validate Python agents for compliance with the Schema-First Empire Constitution.

**Usage:**
```bash
python agents/constitutional_compliance_validator/constitutional_compliance_validator.py \
  --file-path agents/brand_identity_generator/brand_identity_generator.py
```

**Features:**
- Complete constitutional validation
- Detailed compliance reports
- Violation severity scoring
- Actionable recommendations

**Documentation:** [agents/constitutional_compliance_validator/README.md](agents/constitutional_compliance_validator/README.md)

## Quick Start

### Installation
```bash
# Install dependencies
pip install -r requirements.txt

# Set up development environment
make dev-setup
```

### Running Quality Checks
```bash
# Check all agents
make quality-check

# Test specific agents
make test-brand          # Brand identity generator
make test-journey        # Customer journey mapper
make test-constitutional # Constitutional compliance validator

# Test everything
make test-all
```

### Development Commands

**Code Quality:**
```bash
make lint        # Lint all agents
make format      # Format all agents
make type-check  # Type check all agents
```

**Testing:**
```bash
make test                    # Run all tests
make test-contract          # Contract tests only
make test-integration       # Integration tests only
```

**Examples:**
```bash
# Brand identity examples
make example-basic
make example-enhanced

# Customer journey examples
make example-journey-ecommerce
make example-journey-saas

# Constitutional validation examples
make example-validate-brand
make example-validate-journey
```

## Constitutional Framework

All agents in this repository follow the **Schema-First Empire Constitution v1.3.5**, ensuring:

- ✅ **Single-file programs** with organized folder structure
- ✅ **Schema-first design** with JSON contracts
- ✅ **Decision tables** before LLM fallback
- ✅ **Agent Envelope** output format
- ✅ **Type safety** with mypy --strict compliance
- ✅ **Comprehensive testing** (contract, integration, golden)
- ✅ **Performance budgets** and cost tracking
- ✅ **Provider abstraction** for LLM services

**Constitution:** [.specify/memory/constitution.md](.specify/memory/constitution.md)

## Adding New Agents

1. **Create agent folder:**
   ```bash
   mkdir -p agents/my_agent/{schemas,tests/{contract,integration,golden},examples,docs}
   ```

2. **Implement single-file program:**
   ```bash
   # Create agents/my_agent/my_agent.py following constitutional requirements
   ```

3. **Add schemas:**
   ```bash
   # Create agents/my_agent/schemas/input.json
   # Create agents/my_agent/schemas/output.json
   ```

4. **Write tests:**
   ```bash
   # Add contract tests in agents/my_agent/tests/contract/
   # Add integration tests in agents/my_agent/tests/integration/
   # Add golden tests in agents/my_agent/tests/golden/
   ```

5. **Validate compliance:**
   ```bash
   python agents/constitutional_compliance_validator/constitutional_compliance_validator.py \
     --file-path agents/my_agent/my_agent.py
   ```

## Development Workflow

1. **Feature Development**: Use `/specify` and `/plan` commands for new features
2. **Constitutional Compliance**: All agents must pass constitutional validation
3. **Testing**: Comprehensive test coverage (≥80%) required
4. **Documentation**: Each agent has complete README and usage examples
5. **Quality Gates**: Lint, type check, and tests must pass

## Architecture Principles

- **Schema-First**: JSON schemas define all contracts
- **Constitutional**: All code follows constitutional requirements
- **Agent-Oriented**: Self-contained programs with clear boundaries
- **Performance-Aware**: Declared budgets and monitoring
- **Provider-Agnostic**: Switchable LLM providers
- **Observable**: JSONL logging and cost tracking

## License

Part of the Facebook Ads Management System.

---

**Getting Started:** Choose an agent from the list above and check its README for detailed usage instructions.