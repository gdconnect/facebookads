# Quickstart: Content Classification System

**Feature**: 011-intererim-classification-of
**Purpose**: Validate core classification scenarios work end-to-end
**Prerequisites**: Agent implementation complete

## Quick Validation Scenarios

### Scenario 1: Clear Article Classification (Rule-based)
**Test**: High-confidence article classification using rules only
```bash
echo '{"content": "How to Build a Personal Website: A complete step-by-step guide for beginners covering domain registration, hosting setup, and launch strategies."}' | \
python agents/content_classifier/content_classifier.py run
```

**Expected Output**:
```json
{
  "output": {
    "content_type": "article",
    "confidence": 0.9,
    "method": "rule_based",
    "processing_time_ms": "<200",
    "llm_calls_used": 0,
    "reasoning": "Instructional content detected"
  },
  "error": null
}
```

**Success Criteria**:
- ✅ content_type = "article"
- ✅ confidence ≥ 0.7
- ✅ method = "rule_based"
- ✅ processing_time_ms < 200
- ✅ llm_calls_used = 0

### Scenario 2: Clear Essay Classification (Rule-based)
**Test**: High-confidence essay classification using rules only
```bash
echo '{"content": "In my opinion, the digital age has fundamentally changed how we form relationships. I believe that while technology connects us globally, it has also created a paradox of isolation that we must address."}' | \
python agents/content_classifier/content_classifier.py run
```

**Expected Output**:
```json
{
  "output": {
    "content_type": "essay",
    "confidence": 0.9,
    "method": "rule_based",
    "processing_time_ms": "<200",
    "llm_calls_used": 0,
    "reasoning": "Personal opinion detected"
  },
  "error": null
}
```

**Success Criteria**:
- ✅ content_type = "essay"
- ✅ confidence ≥ 0.7
- ✅ method = "rule_based"
- ✅ processing_time_ms < 200
- ✅ llm_calls_used = 0

### Scenario 3: Ambiguous Content with LLM Fallback
**Test**: Low-confidence content triggers LLM classification
```bash
echo '{"content": "The Future of Remote Work. Remote work has transformed modern employment. Companies adapt to distributed teams while employees navigate new challenges and opportunities in this evolving landscape."}' | \
python agents/content_classifier/content_classifier.py run --config '{"model": {"enabled": true}}'
```

**Expected Output**:
```json
{
  "output": {
    "content_type": "article",
    "confidence": 0.8,
    "method": "llm_single",
    "processing_time_ms": "<5000",
    "llm_calls_used": 1,
    "reasoning": "Informational content about work trends..."
  },
  "error": null
}
```

**Success Criteria**:
- ✅ content_type ∈ ["article", "essay"]
- ✅ confidence > 0.5
- ✅ method ∈ ["llm_single", "llm_double"]
- ✅ processing_time_ms < 5000
- ✅ llm_calls_used > 0
- ✅ reasoning field present

### Scenario 4: Interim Classification Request
**Test**: Fast interim classification during content processing
```bash
echo '{"content": "Marketing automation tools help businesses streamline their processes and improve efficiency.", "interim": true, "timeout_ms": 1000}' | \
python agents/content_classifier/content_classifier.py run
```

**Expected Output**:
```json
{
  "output": {
    "content_type": "article",
    "confidence": 0.8,
    "method": "rule_based",
    "processing_time_ms": "<1000",
    "llm_calls_used": 0
  },
  "error": null
}
```

**Success Criteria**:
- ✅ processing_time_ms < 1000 (interim timeout respected)
- ✅ Valid classification returned
- ✅ No timeout errors

### Scenario 5: Batch Classification
**Test**: Multiple content pieces processed efficiently
```bash
echo '{
  "items": [
    {"content": "How to cook pasta: Boil water, add salt, cook noodles for 8-10 minutes."},
    {"content": "I remember my grandmother teaching me to cook. Those moments shaped my love for food."}
  ]
}' | \
python agents/content_classifier/content_classifier.py batch
```

**Expected Output**:
```json
{
  "output": {
    "results": [
      {
        "index": 0,
        "success": true,
        "result": {
          "content_type": "article",
          "confidence": 0.9,
          "method": "rule_based"
        }
      },
      {
        "index": 1,
        "success": true,
        "result": {
          "content_type": "essay",
          "confidence": 0.8,
          "method": "rule_based"
        }
      }
    ],
    "summary": {
      "total_items": 2,
      "successful": 2,
      "failed": 0
    }
  }
}
```

**Success Criteria**:
- ✅ All items classified correctly
- ✅ summary.successful = 2
- ✅ summary.failed = 0

### Scenario 6: Error Handling - Invalid Input
**Test**: Graceful handling of invalid input
```bash
echo '{"content": ""}' | \
python agents/content_classifier/content_classifier.py run
```

**Expected Output**:
```json
{
  "output": null,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Content cannot be empty",
    "retry_possible": false
  }
}
```

**Success Criteria**:
- ✅ output = null
- ✅ error.code = "VALIDATION_ERROR"
- ✅ error.message present
- ✅ error.retry_possible = false

### Scenario 7: LLM Service Unavailable Graceful Degradation
**Test**: System continues working when LLM is unavailable
```bash
echo '{"content": "This is ambiguous content that might need LLM classification."}' | \
python agents/content_classifier/content_classifier.py run --config '{"model": {"enabled": false}}'
```

**Expected Output**:
```json
{
  "output": {
    "content_type": "article",
    "confidence": 0.5,
    "method": "rule_based",
    "processing_time_ms": "<200",
    "llm_calls_used": 0,
    "reasoning": "Default classification (LLM disabled)"
  },
  "error": null
}
```

**Success Criteria**:
- ✅ Valid classification returned (no failure)
- ✅ method = "rule_based"
- ✅ llm_calls_used = 0
- ✅ Lower confidence acceptable

## Performance Validation

### Budget Compliance Check
```bash
time python agents/content_classifier/content_classifier.py selfcheck
```

**Success Criteria**:
- ✅ Runtime < 1s
- ✅ All config validation passes
- ✅ Schema generation works
- ✅ Decision tables load correctly

### Schema Validation
```bash
python agents/content_classifier/content_classifier.py print-schemas
```

**Success Criteria**:
- ✅ Valid JSON schemas output
- ✅ Input/output/envelope schemas present
- ✅ No validation errors

## Integration Validation

### CLI Interface Check
```bash
python agents/content_classifier/content_classifier.py --help
```

**Success Criteria**:
- ✅ run, batch, selfcheck, print-schemas commands available
- ✅ --config, --strict, --log-level flags present
- ✅ Help text clear and complete

### Logging Validation
```bash
echo '{"content": "Test content"}' | \
python agents/content_classifier/content_classifier.py run 2>logs.jsonl
cat logs.jsonl | jq .
```

**Success Criteria**:
- ✅ JSONL logs to STDERR
- ✅ agent_run event present
- ✅ decision_eval events for rules
- ✅ All required fields present (ts, event, agent, version, trace_id)

## Definition of Done

All scenarios must pass with success criteria met:
- [ ] Rule-based article classification (Scenario 1)
- [ ] Rule-based essay classification (Scenario 2)
- [ ] LLM fallback classification (Scenario 3)
- [ ] Interim classification (Scenario 4)
- [ ] Batch processing (Scenario 5)
- [ ] Error handling (Scenario 6)
- [ ] Graceful degradation (Scenario 7)
- [ ] Performance compliance
- [ ] Schema validation
- [ ] CLI interface working
- [ ] Structured logging active

**Ready for Production**: All quickstart scenarios pass + constitutional compliance verified
