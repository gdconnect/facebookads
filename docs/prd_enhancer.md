# Defensive PRD Enhancer
## Minimal Product Requirements Document

**Version:** 1.0  
**Complexity Budget:** 30/100  
**Target Delivery:** 2 weeks  
**Primary Success Metric:** Reduce average PRD implementation time by 50%

---

## 📌 CORE FUNCTIONALITY (Maximum 5)

1. **Ambiguity Detection** - Find vague terms like "user-friendly", "scalable", "fast" and demand specific metrics
2. **Scope Cutting** - Force explicit "NOT doing" list that's 2x longer than "doing" list  
3. **Event Discovery** - Extract maximum 5 domain events from happy path only
4. **Schema Generation** - Create minimal JSON schemas with only required fields
5. **Complexity Scoring** - Output single 0-100 score (lower is better)

## 🚫 EXPLICITLY NOT DOING

- NOT building a web UI or API
- NOT handling multiple file formats (Markdown only)
- NOT generating diagrams or visualizations  
- NOT integrating with project management tools
- NOT tracking changes between PRD versions
- NOT supporting collaborative editing
- NOT generating implementation code
- NOT creating test suites
- NOT handling non-English content
- NOT providing real-time analysis
- NOT supporting PRD templates/frameworks beyond basic structure
- NOT generating cost estimates
- NOT doing competitive analysis
- NOT creating user personas
- NOT generating market research

## 🎯 ONE PRIMARY USE CASE

**Input:** A markdown PRD file with typical product description  
**Output:** Enhanced markdown with ambiguities resolved, scope reduced, and minimal specifications  
**User:** Single product manager or tech lead working locally  
**Success:** PRD can be implemented in half the time with fewer questions

## 📋 MINIMAL SPECIFICATIONS

### Input Schema (Bare Minimum)
```json
{
  "type": "object",
  "properties": {
    "file_path": {"type": "string"}
  },
  "required": ["file_path"]
}
```

### Output Schema (Essential Only)
```json
{
  "type": "object", 
  "properties": {
    "complexity_score": {"type": "number"},
    "core_features": {"type": "array", "maxItems": 5},
    "not_doing": {"type": "array", "minItems": 10},
    "ambiguities_found": {"type": "array"},
    "enhanced_prd": {"type": "string"}
  }
}
```

### Core Events (Happy Path Only)
1. `FileLoaded` - PRD markdown loaded
2. `AmbiguitiesDetected` - Vague terms identified  
3. `ScopeReduced` - Features cut to essential 20%
4. `SpecsGenerated` - Minimal schemas created
5. `PRDEnhanced` - Output file written

## ✅ CRITICAL ACCEPTANCE CRITERIA (Maximum 10)

1. **GIVEN** a PRD with 20 features **WHEN** analyzed **THEN** outputs maximum 5 core features
2. **GIVEN** vague terms like "fast" **WHEN** detected **THEN** demands specific metric (e.g., "<200ms")
3. **GIVEN** a complex PRD **WHEN** enhanced **THEN** complexity score decreases by >30%
4. **GIVEN** any PRD **WHEN** processed **THEN** "not doing" list has 2x more items than "doing" list
5. **GIVEN** a PRD with workflows **WHEN** analyzed **THEN** extracts maximum 5 events
6. **GIVEN** an enhanced PRD **WHEN** reviewed **THEN** fits on 3 pages or less
7. **GIVEN** invalid markdown **WHEN** loaded **THEN** fails fast with clear error
8. **GIVEN** ambiguous requirement **WHEN** found **THEN** provides specific clarification

## 🏗️ IMPLEMENTATION CONSTRAINTS

### Technical Boundaries
- **Single Python file** < 1000 lines
- **Dependencies:** pydantic, pydantic-ai, markdown parser only
- **LLM:** Claude-3-haiku via Pydantic-AI (maximum 3 passes)
- **No database, no external services beyond LLM API**
- **Runs locally, processes single file at a time**
- **Stateless - no memory between runs**

### Simplification Rules
- Use regex for pattern matching when LLM unavailable
- Hard-coded heuristics as fallback for LLM failures  
- Synchronous processing only (even for LLM calls)
- No configuration files - all rules in code
- No plugins or extensions
- Maximum 10 second timeout for all LLM operations

### LLM Integration Strategy (Pydantic-AI)

#### Multi-Pass Refinement Architecture
**Maximum 3 Passes** (Hard limit - no exceptions)

**Pass 1: Ambiguity Detection (Required)**
- **Trigger:** Always runs
- **Agent:** `AmbiguityDetector` with claude-3-haiku (cheapest/fastest)
- **Input:** Raw PRD text chunks (max 500 words each)
- **Output:** List of ambiguous terms with specific clarifications
- **Fallback:** Regex patterns if LLM fails
- **Success Criteria:** Find at least 3 ambiguities or mark as "unusually clear"

**Pass 2: Scope Reduction (Conditional)**
- **Trigger:** Only if PRD has >7 proposed features
- **Agent:** `ScopeGuardian` with claude-3-haiku
- **Input:** Feature list + detected ambiguities
- **Output:** Ranked features by ROI (value/effort ratio)
- **Fallback:** Simple keyword scoring (must/should/could)
- **Success Criteria:** Cut to exactly 5 features

**Pass 3: Contradiction Check (Conditional)**
- **Trigger:** Only if complexity score >50 after Pass 2
- **Agent:** `ConsistencyChecker` with claude-3-haiku  
- **Input:** Reduced feature set
- **Output:** Internal contradictions and conflicts
- **Fallback:** Skip this pass
- **Success Criteria:** Zero contradictions in core features

#### LLM Agent Definitions

```python
# Pydantic-AI Agent Configuration
class AmbiguityDetector(BaseModel):
    """Pass 1: Find vague terms"""
    system_prompt: str = """Find ambiguous terms. Output ONLY:
    - Term: [ambiguous word/phrase]
    - Problem: [why it's vague]  
    - Fix: [specific metric/definition]
    
    Examples:
    - Term: "fast" → Fix: "<200ms response time"
    - Term: "user-friendly" → Fix: "3 clicks to complete task"
    - Term: "scalable" → Fix: "handles 1000 concurrent users"
    
    Max 10 ambiguities. Be harsh."""
    
    max_tokens: int = 200
    temperature: float = 0.3  # Low creativity, high consistency

class ScopeGuardian(BaseModel):
    """Pass 2: Cut features ruthlessly"""
    system_prompt: str = """Score each feature:
    Value: 1-10 (how critical for core use case?)
    Effort: 1-10 (implementation complexity?)
    Score = Value / Effort
    
    Only features with Score >2.0 survive.
    Maximum 5 features output.
    Default to cutting, not keeping."""
    
    max_tokens: int = 150
    temperature: float = 0.2

class ConsistencyChecker(BaseModel):
    """Pass 3: Find contradictions"""
    system_prompt: str = """Find ONLY direct contradictions:
    - Feature A requires X but Feature B prevents X
    - Constraint conflicts with requirement
    
    Output: [Feature A] conflicts with [Feature B] because [reason]
    
    If no contradictions, output: "NONE"
    Max 3 contradictions."""
    
    max_tokens: int = 100
    temperature: float = 0.1  # Nearly deterministic
```

#### Pass Orchestration Rules

1. **Sequential, Never Parallel** - Each pass depends on previous
2. **Fail Fast** - If any pass fails, use fallback immediately
3. **Time Budget** - Total 10 seconds for all LLM calls
4. **Token Budget** - Maximum 1000 tokens total across all passes
5. **No Retry Logic** - If LLM fails, use regex/heuristic immediately

#### When NOT to Use LLM

- **Skip Pass 2 if:** PRD already has ≤5 features
- **Skip Pass 3 if:** Complexity score already <30
- **Skip all passes if:** PRD is <500 words (too simple to need enhancement)
- **Use fallback if:** LLM response time >3 seconds

#### Fallback Strategies (When LLM Unavailable)

```python
# Regex patterns for Pass 1 (Ambiguity Detection)
AMBIGUOUS_TERMS = [
    (r'\b(fast|quick|slow)\b', 'Specify time metric'),
    (r'\b(scalable|performant)\b', 'Specify load metric'),
    (r'\b(user-friendly|intuitive)\b', 'Specify clicks/steps'),
    (r'\b(secure|safe)\b', 'Specify security standard'),
    (r'\b(reliable|robust)\b', 'Specify uptime percentage')
]

# Keyword scoring for Pass 2 (Scope Reduction)  
PRIORITY_KEYWORDS = {
    'must': 10, 'critical': 9, 'core': 8,
    'should': 5, 'nice': 3, 'could': 2,
    'future': 0, 'maybe': 0, 'consider': 0
}

# No fallback for Pass 3 - just skip if LLM unavailable
```

#### LLM Cost Control

- **Model Selection:** claude-3-haiku only (cheapest)
- **Token Limits:** Hard maximum per pass
- **Caching:** Store LLM responses for identical PRD chunks
- **Batching:** Group multiple ambiguities in single call
- **Early Termination:** Stop if first pass finds PRD is already clear

## ⚠️ IMPLEMENTATION WARNINGS

1. **DO NOT** add features during implementation - if it's not listed here, it doesn't exist
2. **DO NOT** handle edge cases - let them fail loudly  
3. **DO NOT** add "nice to have" enhancements
4. **DO NOT** over-engineer for future extensibility
5. **DO NOT** add abstraction layers
6. **PREFER** deletion over addition
7. **PREFER** explicit over flexible
8. **PREFER** failing fast over graceful degradation

## 📊 COMPLEXITY BUDGET ALLOCATION

- Ambiguity Detection (Pass 1): 8/30 points
- Scope Reduction (Pass 2): 7/30 points  
- Consistency Check (Pass 3): 3/30 points
- Event Extraction: 5/30 points
- Schema Generation: 4/30 points
- File I/O & Basic Parsing: 3/30 points

**Total: 30/30** (No buffer - cut features if complexity grows)

## 🎛️ NON-CONFIGURABLE DEFAULTS

These are hard-coded and NOT configurable:

- Maximum 5 core features per PRD
- Maximum 5 events per workflow  
- Maximum 10 ambiguities reported
- Complexity score formula: `(entities * 3) + (events * 2) + (integrations * 5)`
- "Not doing" list must be 2x "doing" list
- Output PRD maximum 3 pages

## 🧪 MANUAL TEST SCENARIOS

1. **Smoke Test:** Run on a 1-paragraph PRD → Should complete in <2 seconds
2. **Complexity Test:** Run on 10-page PRD → Should reduce to 3 pages  
3. **Ambiguity Test:** PRD with "user-friendly UI" → Should demand specific metrics
4. **Scope Test:** PRD with 20 features → Should cut to 5 or fewer
5. **LLM Failure Test:** Disable network → Should use regex fallback
6. **Multi-Pass Test:** Complex PRD → Should trigger all 3 passes
7. **Skip Pass Test:** Simple PRD with 3 features → Should skip Pass 2 & 3

## 📝 EXAMPLE USAGE

```bash
python defensive_prd_enhancer.py product_requirements.md

# Output:
# 🔍 Pass 1: Found 8 ambiguities via LLM
# ✂️ Pass 2: Cut 15 of 20 features (keeping only essential 5)  
# ✅ Pass 3: Skipped (complexity already <30)
# 📊 Complexity score reduced from 85 to 28
# ✅ Enhanced PRD saved to product_requirements_enhanced.md

# With LLM failure:
python defensive_prd_enhancer.py product_requirements.md

# Output:
# 🔍 Pass 1: LLM timeout, using regex fallback
# ✂️ Pass 2: Using keyword scoring (LLM unavailable)
# ⚠️ Fallback mode: Results may be less precise
# 📊 Complexity score reduced from 85 to 35
# ✅ Enhanced PRD saved to product_requirements_enhanced.md
```

## 🔬 LLM Pass Decision Tree

```
START → PRD Loaded
    │
    ├─> Is PRD >500 words? ──No──> Skip all LLM passes
    │   
    Yes
    │
    ├─> PASS 1: Ambiguity Detection (Always)
    │       ├─> Success → Found ambiguities
    │       └─> Timeout/Fail → Use regex patterns
    │
    ├─> Has >7 features? ──No──> Skip Pass 2
    │   
    Yes
    │
    ├─> PASS 2: Scope Reduction
    │       ├─> Success → Features ranked and cut
    │       └─> Timeout/Fail → Use keyword scoring
    │
    ├─> Complexity >50? ──No──> Skip Pass 3
    │   
    Yes
    │
    └─> PASS 3: Consistency Check
            ├─> Success → Contradictions found
            └─> Timeout/Fail → Skip (no fallback)
```

## 🚨 FAILURE MODES (Not Handling)

- Concurrent PRD processing - run sequentially
- Partial failures - start over
- Corrupted markdown - fail with error
- Non-English content - undefined behavior
- LLM rate limits - use regex fallback
- Large files (>1MB) - will be slow, that's okay

## 📅 DEVELOPMENT MILESTONES

**Week 1:**
- Day 1-2: Basic file I/O and markdown parsing
- Day 3-4: Ambiguity detection with regex
- Day 5: Scope reduction logic

**Week 2:**  
- Day 1-2: Event extraction (simple pattern matching)
- Day 3: Minimal schema generation
- Day 4: Complexity scoring
- Day 5: Testing and output formatting

## 🎖️ SUCCESS CRITERIA

**Launch Success = ONE Metric:**
- Implementation time for enhanced PRDs is 50% less than original PRDs

**Failure Indicators:**
- Enhanced PRD is longer than original (immediate failure)
- Complexity score increases (immediate failure)  
- More than 5 features in output (immediate failure)

---

## APPENDIX: What This Tool Will NOT Become

This tool will NEVER:
- Become a "PRD platform"
- Add user management or collaboration
- Generate code or tests
- Integrate with CI/CD
- Support multiple formats
- Add a GUI
- Become configurable
- Support plugins
- Generate reports or analytics
- Become a service or API

**If someone asks for these features, the answer is NO.**

---

*Signed off by:*  
*Product: _________________ Date: _________*  
*Engineering: ______________ Date: _________*  

*Agreement: We will build ONLY what's specified in Core Functionality. Everything else is explicitly excluded.*