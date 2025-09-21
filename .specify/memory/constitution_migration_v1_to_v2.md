# Constitution Migration Guide: v1.4 → v2.0

**Migration Timeline**: 3 months (until 2025-12-21)
**Breaking Changes**: Yes - complexity tiers, mandatory README, PydanticAI patterns
**Backward Compatibility**: 90% preserved, new requirements added

---

## 🎯 What Changed in v2.0

### Major Changes
1. **Complexity Tiers**: 3-tier system with appropriate requirements
2. **Mandatory PydanticAI**: All LLM functionality must use PydanticAI exclusively
3. **Mandatory README.md**: Every agent needs developer-focused documentation
4. **Streamlined Patterns**: Standard patterns for common scenarios
5. **Flexible Requirements**: Simple agents have fewer requirements

### Benefits
- **Reduced friction** for simple agents (less boilerplate)
- **Provider switching** without code changes via PydanticAI
- **Better developer experience** with mandatory README files
- **Practical patterns** for common implementation challenges
- **Maintained quality** for complex/critical agents

---

## 📊 Agent Classification

### Step 1: Classify Your Agent

Determine your agent's complexity tier:

```python
# Count these metrics for your agent:
lines_of_code = len([line for line in open('agent.py') if line.strip() and not line.strip().startswith('#')])
has_external_apis = bool(httpx_imports or requests_imports or api_calls)
has_llm = bool(openai_imports or anthropic_imports or model_calls)
is_production_critical = bool(revenue_impact or user_facing)

# Determine tier:
if lines_of_code < 200 and not has_external_apis:
    tier = 1  # Simple
elif lines_of_code < 500 or has_external_apis or has_llm:
    tier = 2  # Standard
else:
    tier = 3  # Critical
```

### Step 2: Requirements by Tier

| Requirement | Tier 1 | Tier 2 | Tier 3 |
|-------------|---------|---------|---------|
| README.md | ✅ Basic | ✅ Complete | ✅ Comprehensive |
| Decision Tables | ❌ Optional | ⚠️ If >5 rules | ✅ Required |
| Schema Generation | ❌ No | ✅ Yes | ✅ Yes |
| Testing | Basic (2 tests) | Balanced | Comprehensive |
| Type Checking | `mypy` basic | `mypy --strict` | `mypy --strict` (no ignores) |
| Coverage | 70% | 80% | 90% |

---

## 🔧 Migration Steps

### For All Agents

#### 1. Create README.md (MANDATORY)
```bash
# Create from template
cat > README.md << 'EOF'
# Your Agent Name

One-line description of what this agent does.

## Quick Start

```bash
pip install -r requirements.txt
echo "input content" | python your_agent.py run
```

## Usage

### Basic Example
```bash
python your_agent.py run --input "your content"
```

## Development

```bash
pytest                     # Run tests
mypy your_agent.py        # Type check
python your_agent.py selfcheck  # Validate
```
EOF
```

#### 2. Update Header Docstring
```python
#!/usr/bin/env python3
"""
Your Agent Name - Constitutional Single-File Python Agent (v2.0)

PURPOSE:
Brief description of what the agent does.

COMPLEXITY TIER: {1|2|3}  # REQUIRED declaration

USAGE:
    echo "input" | python your_agent.py run

BUDGETS:
- Runtime: <X seconds
- Memory: <Y MB
# For LLM agents, add:
- LLM calls: ≤2 per request
- Tokens: ≤2000 per request
- Cost: ≤$0.01 per request
"""
```

#### 3. Add Complexity Tier Declaration
```python
# Add near the top of your file
AGENT_COMPLEXITY_TIER = 1  # or 2 or 3
```

### For LLM-Enabled Agents

#### 4. Migrate to PydanticAI (MANDATORY)

**Before (v1.4 - Custom LLM):**
```python
import openai

def call_llm(prompt: str) -> str:
    response = openai.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content
```

**After (v2.0 - PydanticAI):**
```python
from pydantic_ai import Agent
from pydantic import BaseModel

class LLMResult(BaseModel):
    result: str
    confidence: float

def create_classification_agent(config: Config) -> Agent:
    provider_map = {
        "openai": f"openai:{config.model.name}",
        "anthropic": f"anthropic:{config.model.name}",
        "gemini": f"gemini:{config.model.name}",
    }

    return Agent(
        provider_map.get(config.model.provider),
        result_type=LLMResult,
        system_prompt="Your system prompt here"
    )

# Standard usage pattern
agent = create_classification_agent(config)
result = await agent.run(input_text)
```

#### 5. Add Standard LLM Configuration
```python
@dataclass
class ModelConfig:
    enabled: bool = False
    provider: str = "openai"
    name: str = "gpt-4o-mini"
    api_key_env: str = "OPENAI_API_KEY"
    base_url: str | None = None
    timeout_s: int = 30
    max_tokens: int = 2000
    temperature: float = 0.1
```

#### 6. Update README for LLM Support
Add this section to your README.md:
```markdown
## LLM Configuration

### Quick Setup
```bash
# OpenAI (default)
export OPENAI_API_KEY=sk-...
export LLM_ENABLED=true

# Or Anthropic
export ANTHROPIC_API_KEY=sk-ant-...
export AGENT_MODEL_PROVIDER=anthropic
```

### Supported Providers
- OpenAI (gpt-4o, gpt-4o-mini)
- Anthropic (claude-3-opus, claude-3-sonnet, claude-3-haiku)
- Google (gemini-pro)
- Local (OpenAI-compatible endpoints)
```

### For Tier 2 & 3 Agents

#### 7. Ensure Schema Generation Works
```bash
# Test schema generation
python your_agent.py print-schemas

# Should output JSON schemas for input/output/envelope
```

#### 8. Update Testing Structure
```bash
# Tier 2: Organize tests
mkdir -p tests/{unit,integration,golden}

# Tier 3: Add comprehensive tests
mkdir -p tests/{contract,golden,integration,performance,unit}
```

---

## 🚀 Provider Switching Benefits

### Before v2.0 (Code Changes Required)
```python
# Had to modify code to switch providers
import openai  # Hardcoded provider
client = openai.OpenAI()  # Provider-specific code
```

### After v2.0 (Config-Only Switching)
```bash
# Switch to Anthropic (no code changes)
export AGENT_MODEL_PROVIDER=anthropic
export AGENT_MODEL_NAME=claude-3-haiku
export ANTHROPIC_API_KEY=sk-ant-...

# Switch to local model (no code changes)
export AGENT_MODEL_PROVIDER=local
export AGENT_MODEL_BASE_URL=http://localhost:8080

# Switch to Groq (no code changes)
export AGENT_MODEL_PROVIDER=groq
export AGENT_MODEL_NAME=mixtral-8x7b-32768
export GROQ_API_KEY=gsk_...
```

---

## ✅ Validation Checklist

### All Agents
- [ ] README.md created with required sections
- [ ] Complexity tier declared in header
- [ ] Header docstring updated with budgets
- [ ] Appropriate testing for tier
- [ ] Code quality gates pass for tier

### LLM-Enabled Agents
- [ ] Migrated to PydanticAI exclusively
- [ ] Standard agent factory pattern implemented
- [ ] Typed response models defined
- [ ] Cost tracking pattern implemented
- [ ] Graceful degradation when PydanticAI unavailable
- [ ] LLM section added to README
- [ ] Provider switching tested

### Tier 2 & 3 Only
- [ ] Schema generation working (`print-schemas`)
- [ ] Decision tables appropriate for complexity
- [ ] Test structure organized properly

---

## 🔍 Common Migration Issues

### Issue 1: Type Ignores
**Problem**: Too many `# type: ignore` comments
**Solution**: v2.0 allows more flexibility:
- Tier 1: Up to 10 ignores with justification
- Tier 2: Up to 5 ignores with justification
- Tier 3: Zero ignores (strict compliance)

### Issue 2: PydanticAI Import Errors
**Problem**: PydanticAI not available in environment
**Solution**: Add graceful degradation:
```python
try:
    from pydantic_ai import Agent
    PYDANTIC_AI_AVAILABLE = True
except ImportError:
    PYDANTIC_AI_AVAILABLE = False

# Later in code:
if config.model.enabled and PYDANTIC_AI_AVAILABLE:
    return llm_result
else:
    return rule_based_result
```

### Issue 3: Complex Testing Requirements
**Problem**: Too many test files required
**Solution**: v2.0 has tier-appropriate testing:
- Tier 1: Just 2 basic tests
- Tier 2: Balanced testing (3-5 tests)
- Tier 3: Comprehensive (full test suite)

### Issue 4: Decision Table Overhead
**Problem**: Simple logic forced into decision tables
**Solution**: v2.0 allows simple conditionals for Tier 1:
```python
# Tier 1: Simple conditionals allowed
if "tutorial" in content.lower():
    return "article"
elif "story" in content.lower():
    return "story"
else:
    return "article"  # default
```

---

## 📅 Migration Timeline

### Month 1 (Oct 2025)
- [ ] All agents get README.md
- [ ] Complexity tiers declared
- [ ] LLM agents migrate to PydanticAI

### Month 2 (Nov 2025)
- [ ] Testing structures updated
- [ ] Code quality gates adjusted per tier
- [ ] Provider switching validated

### Month 3 (Dec 2025)
- [ ] Final validation
- [ ] Documentation review
- [ ] v1.4 sunset

### After Dec 21, 2025
- New agents MUST follow v2.0
- v1.4 agents flagged for migration in CI
- No new v1.4 agents accepted

---

## 🆘 Getting Help

### Migration Support
1. **Review existing agents** that have migrated
2. **Copy patterns** from reference implementations
3. **Test incrementally** (don't migrate everything at once)
4. **Use templates** provided in this guide

### Validation Commands
```bash
# Check your agent tier
python your_agent.py selfcheck

# Validate README
grep -q "Quick Start" README.md

# Test provider switching (LLM agents)
export AGENT_MODEL_PROVIDER=anthropic
python your_agent.py selfcheck
```

The v2.0 constitution is designed to reduce friction while maintaining quality. Focus on your agent's complexity tier and implement only the requirements that make sense for your use case.