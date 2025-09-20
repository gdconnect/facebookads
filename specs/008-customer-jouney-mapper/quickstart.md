# Quickstart: Customer Journey Mapper Generator

**Date**: 2025-09-20
**Purpose**: Validate customer journey mapper implementation

## Overview

This quickstart provides step-by-step validation scenarios for the customer journey mapper generator, covering all major user workflows and edge cases.

## Prerequisites

1. Python 3.11+ installed
2. Customer journey mapper agent (`customer_journey_mapper.py`) implemented
3. Test data files available
4. Schema validation tools available

## Quick Start Commands

### Basic Usage

```bash
# Generate journey map from natural language description
python customer_journey_mapper.py \
  --input "Eco-conscious millennials buying sustainable fashion online" \
  --output journey_map.json

# Generate with structured input
python customer_journey_mapper.py \
  --input-file market_spec.json \
  --output journey_map.json \
  --format json

# Generate with markdown input
python customer_journey_mapper.py \
  --input-file market_description.md \
  --input-format text/markdown \
  --output journey_map.json
```

## Validation Scenarios

### Scenario 1: B2C E-commerce Journey

**User Story**: Business analyst needs customer journey for sustainable fashion brand

**Input**:
```bash
python customer_journey_mapper.py \
  --input "Eco-conscious millennials aged 25-35 shopping for sustainable fashion. They prioritize ethical manufacturing and are willing to pay premium for quality. Primary channels are Instagram and online shopping." \
  --brand-token sustainable_fashion \
  --output ecommerce_journey.json
```

**Expected Output Validation**:
- ✅ Valid JSON conforming to customer_journey.json.schema
- ✅ Persona with millennial demographics and sustainability goals
- ✅ Journey stages: Awareness → Consideration → Purchase → Retention → Advocacy
- ✅ Touchpoints include social media, website, email channels
- ✅ Emotions progress from excited (awareness) to satisfied (advocacy)
- ✅ Pain points include trust, price comparison, delivery concerns
- ✅ Metadata populated with industry="ecommerce", tags=["sustainable", "fashion"]

**Validation Commands**:
```bash
# Schema validation
python -c "import json, jsonschema; jsonschema.validate(json.load(open('ecommerce_journey.json'))['output'], json.load(open('schemas/customer_journey.json.schema')))"

# Required fields check
jq '.output | has("journeyId") and has("persona") and has("stages") and has("metadata")' ecommerce_journey.json

# Stage sequence validation
jq '.output.stages | map(.stageName) | join(" -> ")' ecommerce_journey.json
```

### Scenario 2: B2B SaaS Journey

**User Story**: Product manager needs journey map for accounting software

**Input**:
```bash
python customer_journey_mapper.py \
  --input-file b2b_saas_spec.json \
  --output saas_journey.json \
  --strict
```

**Test Input File** (`b2b_saas_spec.json`):
```json
{
  "market_description": "Small business owners seeking cloud-based accounting solutions",
  "industry": "saas",
  "target_demographics": {
    "occupation": "Small business owners",
    "company_size": "1-50 employees"
  },
  "product_service": "Cloud accounting software with automated bookkeeping",
  "business_model": "B2B"
}
```

**Expected Output Validation**:
- ✅ B2B-specific journey stages including Trial and Onboarding
- ✅ Longer journey duration (weeks to months)
- ✅ Professional channels (email, demos, sales calls)
- ✅ Business-focused pain points (integration, training, ROI)
- ✅ Success metrics include conversion rates and retention

### Scenario 3: Markdown Input Processing

**User Story**: Marketing team provides journey requirements in markdown format

**Input File** (`healthcare_market.md`):
```markdown
# Healthcare Telemedicine Market

## Target Market
Healthcare professionals working in rural clinics who need remote consultation capabilities.

## Demographics
- **Age**: 35-55 years
- **Location**: Rural areas, small towns
- **Occupation**: General practitioners, nurse practitioners
- **Tech Comfort**: Moderate to high

## Product
HIPAA-compliant telemedicine platform with:
- Video consultations
- Electronic health records integration
- Prescription management
- Insurance billing

## Business Model
B2B SaaS with per-provider monthly subscriptions.

## Key Challenges
- Internet connectivity limitations
- Regulatory compliance requirements
- Patient adoption resistance
- Integration with existing systems
```

**Command**:
```bash
python customer_journey_mapper.py \
  --input-file healthcare_market.md \
  --input-format text/markdown \
  --output healthcare_journey.json \
  --log-level debug
```

**Expected Output Validation**:
- ✅ Markdown successfully normalized to structured input
- ✅ Healthcare-specific regulations and compliance considerations
- ✅ Technology adoption challenges reflected in pain points
- ✅ Professional service delivery model in journey stages

### Scenario 4: Error Handling and Edge Cases

**Test Cases**:

```bash
# Empty input
echo '{"market_description": ""}' | python customer_journey_mapper.py --input-file - --output error_test.json
# Expected: Error message about minimum description length

# Invalid JSON input
echo '{"invalid": json}' | python customer_journey_mapper.py --input-file - --output error_test.json
# Expected: JSON parsing error with helpful message

# Missing required fields
echo '{"industry": "saas"}' | python customer_journey_mapper.py --input-file - --output error_test.json
# Expected: Validation error about missing market_description

# Unsupported industry
echo '{"market_description": "Test market", "industry": "unsupported"}' | python customer_journey_mapper.py --input-file - --output error_test.json
# Expected: Industry enum validation error or fallback to "other"
```

### Scenario 5: Performance Validation

**Load Test**:
```bash
# Performance benchmark
time python customer_journey_mapper.py \
  --input "Tech-savvy professionals seeking productivity tools" \
  --output perf_test.json

# Expected: Completion in <5 seconds
```

**Token Usage Test**:
```bash
# Run with cost tracking
python customer_journey_mapper.py \
  --input "Digital nomads looking for travel planning apps" \
  --output token_test.json \
  --log-level info

# Check cost in output
jq '.meta.cost' token_test.json
# Expected: Reasonable token usage (<2000 tokens total)
```

## Integration Test Scenarios

### Contract Test Validation

```bash
# Test schema compliance
python -m pytest tests/contract/test_schema_compliance.py -v

# Test input/output contracts
python -m pytest tests/contract/test_journey_generation.py -v

# Test decision table coverage
python -m pytest tests/contract/test_decision_tables.py -v
```

### Golden Test Validation

```bash
# Run golden tests (deterministic outputs)
python -m pytest tests/integration/test_golden_journeys.py -v

# Compare against reference outputs
python -m pytest tests/integration/test_regression.py -v
```

## Success Criteria Checklist

### Functional Requirements
- [ ] **FR-001**: Accepts various input formats (text, JSON, markdown)
- [ ] **FR-002**: Generates schema-compliant journey maps
- [ ] **FR-003**: Creates realistic customer personas
- [ ] **FR-004**: Covers complete customer lifecycle
- [ ] **FR-005**: Populates relevant touchpoints
- [ ] **FR-006**: Assigns appropriate emotions and pain points
- [ ] **FR-007**: Identifies improvement opportunities
- [ ] **FR-008**: Includes cross-channel analysis when relevant
- [ ] **FR-009**: Populates all required metadata fields

### Performance Requirements
- [ ] Execution time <5 seconds for standard inputs
- [ ] LLM calls ≤2 per execution
- [ ] Memory usage <100MB
- [ ] Token usage <2000 tokens per execution

### Quality Requirements
- [ ] Schema validation passes 100%
- [ ] All golden tests pass
- [ ] Error handling graceful and informative
- [ ] Output deterministic for same input
- [ ] Constitutional compliance verified

### Usability Requirements
- [ ] Clear CLI interface with help text
- [ ] Meaningful error messages
- [ ] Multiple output format options
- [ ] Validation tools available

## Troubleshooting

### Common Issues

**Schema Validation Failures**:
```bash
# Check schema compliance
python -c "
import json, jsonschema
try:
    data = json.load(open('journey_map.json'))
    schema = json.load(open('schemas/customer_journey.json.schema'))
    jsonschema.validate(data['output'], schema)
    print('✅ Schema validation passed')
except Exception as e:
    print(f'❌ Schema validation failed: {e}')
"
```

**Performance Issues**:
```bash
# Enable debug logging
python customer_journey_mapper.py --input "..." --log-level debug

# Check for excessive LLM calls in logs
grep "llm_call" stderr.log | wc -l
```

**Missing Fields**:
```bash
# Check required fields
jq '.output | keys' journey_map.json

# Validate metadata completeness
jq '.output.metadata | has("createdDate") and has("version")' journey_map.json
```

## Next Steps

After successful quickstart validation:

1. **Performance Optimization**: Profile and optimize slow operations
2. **Template Expansion**: Add more industry-specific templates
3. **Integration**: Connect with downstream journey analysis tools
4. **Monitoring**: Set up production observability and alerting

## Quickstart Completion

✅ All validation scenarios defined
✅ Success criteria specified
✅ Error handling cases covered
✅ Performance benchmarks established
✅ Integration test framework outlined
✅ Troubleshooting guide provided

**Ready for**: Task generation and implementation phase