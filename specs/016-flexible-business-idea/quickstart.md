# Quickstart: Flexible Business Idea Generator

**Feature**: 016-flexible-business-idea
**Prerequisites**: None (enhancement to existing BIE agent)

## Overview
Test the enhanced Business Idea Evaluator's ability to parse markdown documents with varied structures and section names.

## Test Scenarios

### Scenario 1: Alternative Section Names
**Goal**: Verify the system handles different section naming conventions.

**Test Document** (`test-alt-sections.md`):
```markdown
# FoodTech Revolution

## The Challenge We Face
Restaurants struggle with food waste, losing 30% of ingredients daily due to poor inventory management and unpredictable demand patterns.

## Our Approach
An AI-powered inventory management system that predicts demand based on weather, local events, and historical patterns, reducing waste by 60%.

## Who We Serve
Independent restaurants with 20-150 seats, particularly those in urban areas with high foot traffic variability.

## Revenue Strategy
SaaS model with $99/month per location, plus premium analytics at $199/month for multi-location chains.

## How It Works
IoT sensors track ingredient usage, machine learning models predict demand, and automated ordering prevents stockouts while minimizing waste.
```

**Expected Behavior**:
1. "The Challenge We Face" → maps to `problem` field
2. "Our Approach" → maps to `solution` field
3. "Who We Serve" → maps to `target_customer` field
4. "Revenue Strategy" → maps to `monetization` field
5. "How It Works" → maps to `technical_approach` field

**Test Commands**:
```bash
# Test with current implementation (should fail)
python agents/bie/bie.py evaluate test-alt-sections.md

# Test with enhanced implementation (should succeed)
python agents/bie/bie.py evaluate test-alt-sections.md --enhanced
```

**Success Criteria**:
- ✅ All fields extracted correctly
- ✅ Confidence score > 0.8
- ✅ Strategy used: FUZZY_MATCH or EXACT_MATCH
- ✅ No extraction errors
- ✅ Processing time < 200ms

### Scenario 2: Nested Structure
**Goal**: Test hierarchical content detection.

**Test Document** (`test-nested.md`):
```markdown
# GreenTech Startup

## Market Analysis
### Current Problems
- 40% of urban commuters drive alone
- Public transport unreliable in 60% of cities
- Carbon emissions from transport growing 5% annually

### Our Solution Framework
#### Primary Approach
Real-time rideshare matching with AI optimization
#### Secondary Features
- Carbon footprint tracking
- Gamified rewards system
- Integration with public transport

## Business Model
### Target Users
Urban professionals aged 25-45 with environmental consciousness
### Monetization Approach
- 15% commission per ride
- Premium subscriptions at $9.99/month
- Corporate partnerships for employee programs
```

**Expected Behavior**:
1. Extract problem from nested "Current Problems" section
2. Extract solution from "Our Solution Framework"
3. Handle multiple subsections correctly
4. Map "Target Users" and "Monetization Approach" appropriately

**Success Criteria**:
- ✅ Nested content correctly extracted
- ✅ Multiple subsections consolidated
- ✅ Strategy used: HIERARCHICAL or HYBRID
- ✅ Confidence score > 0.7

### Scenario 3: Missing Optional Fields
**Goal**: Verify graceful handling of incomplete documents.

**Test Document** (`test-minimal.md`):
```markdown
# Simple Idea

## Problem
Students can't find study groups easily on campus.

## Solution
A mobile app that matches students based on courses, schedules, and study preferences using location-based services.
```

**Expected Behavior**:
1. Successfully extract required fields (problem, solution)
2. Generate warnings for missing optional fields
3. Still produce valid RawIdea output
4. Provide helpful suggestions

**Success Criteria**:
- ✅ Valid RawIdea extracted
- ✅ Warnings for missing fields (target_customer, monetization, etc.)
- ⚠️ Suggestions provided for improvement
- ✅ No fatal errors

### Scenario 4: Ambiguous Content (LLM Fallback)
**Goal**: Test LLM fallback for unclear structure.

**Test Document** (`test-ambiguous.md`):
```markdown
# Revolutionary Concept

This innovative platform addresses the growing disconnect between traditional retail and modern consumer expectations. By leveraging cutting-edge technology, we create seamless experiences.

The market opportunity is vast - retail technology solutions represent a $50B market growing at 15% CAGR. Our unique approach combines AI, IoT, and blockchain.

We target progressive retailers ready to embrace digital transformation, particularly mid-market chains with $10-100M revenue seeking competitive advantage.

Our business model centers on subscription licensing with implementation services, generating recurring revenue while ensuring customer success.
```

**Expected Behavior**:
1. Low confidence from rule-based extraction
2. Trigger LLM fallback (if enabled)
3. Extract semantic meaning from unstructured content
4. Generate appropriate warnings about structure

**Success Criteria**:
- ✅ Strategy used: LLM_FALLBACK
- ✅ Valid fields extracted despite poor structure
- ⚠️ Warnings about document structure
- ✅ Processing time < 2 minutes (due to LLM call)

### Scenario 5: Error Handling
**Goal**: Test error cases and validation.

**Test Document** (`test-invalid.md`):
```markdown
# No Content

This document has a title but no clear business idea structure.
Random paragraph about various topics without organization.
```

**Expected Behavior**:
1. Fail to find required fields
2. Generate detailed error messages
3. Provide actionable suggestions
4. Return null RawIdea with error details

**Success Criteria**:
- ❌ RawIdea is null
- ✅ Detailed extraction errors provided
- ✅ Actionable suggestions included
- ✅ Error messages are user-friendly

## Configuration Testing

### Test Fuzzy Matching Thresholds
```bash
# Strict matching (fewer matches, higher precision)
python agents/bie/bie.py evaluate test.md --fuzzy-threshold 0.9

# Relaxed matching (more matches, lower precision)
python agents/bie/bie.py evaluate test.md --fuzzy-threshold 0.6
```

### Test Confidence Thresholds
```bash
# Force LLM fallback with low threshold
python agents/bie/bie.py evaluate test.md --confidence-threshold 0.9 --llm-enabled

# Avoid LLM with high threshold
python agents/bie/bie.py evaluate test.md --confidence-threshold 0.3 --llm-disabled
```

## Performance Validation

### Benchmark Large Documents
```bash
# Generate 2000-line test document
python scripts/generate_large_test.py --lines 2000 > large-test.md

# Measure performance
time python agents/bie/bie.py evaluate large-test.md --performance-mode
```

**Performance Targets**:
- Parsing time < 200ms for typical documents
- Memory usage < 50MB per document
- Handle up to 2000 lines without errors

### Load Testing
```bash
# Process multiple documents in sequence
for i in {1..10}; do
    python agents/bie/bie.py evaluate test-$i.md
done | grep "processing_time_ms"
```

## Integration Testing

### Backward Compatibility
```bash
# Verify existing functionality still works
python agents/bie/bie.py evaluate docs/faith_connect.md --legacy-mode
python agents/bie/bie.py evaluate docs/faith_connect.md --enhanced-mode

# Compare outputs
diff legacy-output.json enhanced-output.json
```

### Schema Validation
```bash
# Export and validate schemas
python agents/bie/bie.py print-schemas > schemas.json
jsonschema -i test-output.json schemas.json
```

## Success Metrics

### Functional Success
- [ ] All 5 test scenarios pass
- [ ] Backward compatibility maintained
- [ ] Configuration options work correctly
- [ ] Error handling provides actionable feedback

### Performance Success
- [ ] Parsing time < 200ms for typical documents
- [ ] Memory usage < 50MB per extraction
- [ ] Can process 2000-line documents
- [ ] No memory leaks in batch processing

### Quality Success
- [ ] Confidence scores reflect extraction quality
- [ ] LLM fallback only triggered when appropriate
- [ ] Section mapping accuracy > 90%
- [ ] User error messages are helpful

## Deployment Validation

### Pre-deployment Checklist
```bash
# Run full test suite
python -m pytest agents/bie/tests/ -v

# Validate with real documents
python agents/bie/bie.py evaluate docs/faith_connect.md
python agents/bie/bie.py evaluate examples/*.md

# Performance regression testing
python scripts/benchmark_bie.py --baseline --enhanced

# Schema validation
python agents/bie/bie.py print-schemas | jq . > /dev/null
```

### Post-deployment Monitoring
- Monitor extraction success rates
- Track confidence score distributions
- Analyze LLM fallback usage frequency
- Monitor processing times and memory usage

## Troubleshooting

### Common Issues
1. **Low confidence scores**: Check section header mapping rules
2. **LLM fallback overuse**: Adjust confidence threshold
3. **Slow processing**: Profile large document handling
4. **Extraction errors**: Validate document structure requirements

### Debug Commands
```bash
# Enable verbose logging
python agents/bie/bie.py evaluate test.md --log-level DEBUG

# Test specific strategies
python agents/bie/bie.py evaluate test.md --strategy FUZZY_MATCH

# Analyze extraction details
python agents/bie/bie.py evaluate test.md --output json | jq .extraction_result
```
