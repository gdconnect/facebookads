# Quickstart: Enhanced Article Outline Generator with Interim Classification

**Feature**: 012-the-changes-are
**Purpose**: Validate enhanced classification capabilities work end-to-end
**Prerequisites**: Agent enhancement implementation complete

## Quick Validation Scenarios

### Scenario 1: Backward Compatibility - Existing Behavior Preserved
**Test**: Verify existing functionality works identically with enhancements
```bash
echo '{
  "content": "# How to Build a Personal Website\n\nThis comprehensive guide covers domain registration, hosting setup, and launch strategies for beginners.",
  "target_depth": 3,
  "include_word_counts": true
}' | python agents/article_outline_generator/article_outline_generator.py run
```

**Expected Output**:
```json
{
  "meta": {
    "agent": "article_outline_generator",
    "version": "1.0.0",
    "cost": {"tokens_in": 25, "tokens_out": 0, "usd": 0.0, "llm_calls": 0},
    "classification_enhanced": false,
    "fallback_used": false
  },
  "input": {...},
  "output": {
    "meta": {
      "content_type": "article",
      "classification_confidence": 0.9,
      "classification_method": "rule_based",
      "classification_reasoning": "Instructional content",
      "llm_calls_used": 0,
      "processing_time_ms": "<200"
    },
    "outline": [...]
  },
  "error": null
}
```

**Success Criteria**:
- ✅ Identical outline generation behavior
- ✅ High confidence rule-based classification (≥0.9)
- ✅ No LLM calls made (llm_calls_used = 0)
- ✅ Processing time <200ms
- ✅ New metadata fields populated correctly

### Scenario 2: Enhanced Classification - Low Confidence Content
**Test**: Content that triggers LLM enhancement due to low rule-based confidence
```bash
echo '{
  "content": "The Future of Remote Work. Remote work has transformed modern employment. Companies adapt to distributed teams while employees navigate new challenges and opportunities in this evolving landscape.",
  "target_depth": 2
}' | python agents/article_outline_generator/article_outline_generator.py run --config '{"model": {"enabled": true}}'
```

**Expected Output**:
```json
{
  "meta": {
    "agent": "article_outline_generator",
    "version": "1.0.0",
    "cost": {"tokens_in": 50, "tokens_out": 30, "usd": 0.002, "llm_calls": 1},
    "classification_enhanced": true,
    "fallback_used": false
  },
  "output": {
    "meta": {
      "content_type": "article",
      "classification_confidence": 0.85,
      "classification_method": "llm_single",
      "classification_reasoning": "LLM enhanced: Informational content about workplace trends and analysis",
      "key_indicators": ["analysis", "trends", "workplace"],
      "llm_calls_used": 1,
      "processing_time_ms": "<5000"
    },
    "outline": [...]
  },
  "error": null
}
```

**Success Criteria**:
- ✅ Enhanced classification used (classification_enhanced = true)
- ✅ Improved confidence score (>0.8)
- ✅ LLM call recorded (llm_calls_used = 1)
- ✅ Cost tracking accurate (usd > 0)
- ✅ Processing time <5s

### Scenario 3: Interim Classification Request
**Test**: Request interim classification during processing workflow
```bash
echo '{
  "content": "Marketing automation tools help businesses streamline their processes and improve efficiency. These tools integrate with existing systems to provide seamless workflow management.",
  "interim": true,
  "timeout_ms": 2000,
  "classification_method": "auto"
}' | python agents/article_outline_generator/article_outline_generator.py run
```

**Expected Output**:
```json
{
  "output": {
    "meta": {
      "content_type": "article",
      "classification_confidence": 0.8,
      "classification_method": "rule_based",
      "classification_reasoning": "Business/technical content",
      "llm_calls_used": 0,
      "processing_time_ms": "<2000",
      "interim_available": true
    },
    "outline": [...]
  }
}
```

**Success Criteria**:
- ✅ Interim classification completed within timeout
- ✅ interim_available = true in metadata
- ✅ Processing time <2000ms (respects timeout)
- ✅ Valid classification provided

### Scenario 4: Story Classification Enhancement
**Test**: Story content that gets enhanced classification
```bash
echo '{
  "content": "In a kingdom far away, a young mage discovered an ancient pendant with mysterious powers. As she learned to harness its magic, she faced challenges that would test her courage and determination.",
  "target_depth": 4
}' | python agents/article_outline_generator/article_outline_generator.py run --config '{"model": {"enabled": true}}'
```

**Expected Output**:
```json
{
  "output": {
    "meta": {
      "content_type": "story",
      "classification_confidence": 0.9,
      "classification_method": "rule_based",
      "classification_reasoning": "Fantasy story elements",
      "key_indicators": ["kingdom", "mage", "pendant", "magic", "powers"],
      "llm_calls_used": 0,
      "processing_time_ms": "<200"
    },
    "outline": [
      {
        "title": "Opening",
        "level": 1,
        "summary": "Introduce the kingdom and the young mage"
      },
      {
        "title": "Discovery",
        "level": 1,
        "summary": "Finding the ancient pendant"
      },
      {
        "title": "Development",
        "level": 1,
        "summary": "Learning to use magical powers"
      },
      {
        "title": "Climax",
        "level": 1,
        "summary": "Facing the ultimate challenge"
      }
    ]
  }
}
```

**Success Criteria**:
- ✅ Story classification (content_type = "story")
- ✅ High confidence without LLM (≥0.9)
- ✅ Story-appropriate outline structure
- ✅ Key fantasy indicators detected

### Scenario 5: Graceful Degradation - LLM Service Unavailable
**Test**: System continues working when LLM enhancement fails
```bash
echo '{
  "content": "This is intentionally ambiguous content that might need LLM enhancement to classify properly.",
  "classification_method": "auto"
}' | OPENAI_API_KEY="" python agents/article_outline_generator/article_outline_generator.py run --config '{"model": {"enabled": true}}'
```

**Expected Output**:
```json
{
  "meta": {
    "classification_enhanced": false,
    "fallback_used": true
  },
  "output": {
    "meta": {
      "content_type": "article",
      "classification_confidence": 0.5,
      "classification_method": "rule_based",
      "classification_reasoning": "Default classification (LLM unavailable)",
      "llm_calls_used": 0,
      "processing_time_ms": "<200"
    },
    "outline": [...]
  },
  "error": null
}
```

**Success Criteria**:
- ✅ Graceful fallback to rule-based classification
- ✅ No service failure (error = null)
- ✅ fallback_used = true in metadata
- ✅ Lower confidence acceptable (≥0.5)
- ✅ Valid outline still generated

### Scenario 6: Error Handling - Invalid Input
**Test**: Proper error handling for invalid requests
```bash
echo '{
  "content": "",
  "interim": true
}' | python agents/article_outline_generator/article_outline_generator.py run
```

**Expected Output**:
```json
{
  "meta": {
    "agent": "article_outline_generator",
    "version": "1.0.0",
    "cost": {"tokens_in": 0, "tokens_out": 0, "usd": 0.0, "llm_calls": 0}
  },
  "input": {"content": "", "interim": true},
  "output": null,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Content cannot be empty or whitespace-only",
    "details": {"field": "content", "value": ""}
  }
}
```

**Success Criteria**:
- ✅ Proper validation error returned
- ✅ No processing attempted (cost = 0)
- ✅ Clear error message
- ✅ Agent Envelope structure maintained

### Scenario 7: Performance Budget Compliance
**Test**: Verify enhanced agent meets constitutional performance requirements
```bash
time python agents/article_outline_generator/article_outline_generator.py selfcheck
```

**Expected Output**:
```bash
# Runtime < 1s
real    0m0.5s
user    0m0.3s
sys     0m0.1s

# JSON output with validation results
{
  "config_valid": true,
  "schemas_generated": true,
  "llm_config_valid": true,
  "performance_budgets_ok": true,
  "constitutional_compliance": "PASS"
}
```

**Success Criteria**:
- ✅ Selfcheck completes in <1s
- ✅ All configuration validation passes
- ✅ Schema generation works correctly
- ✅ Performance budgets verified
- ✅ Constitutional compliance confirmed

### Scenario 8: Schema Validation
**Test**: Enhanced schemas are valid and complete
```bash
python agents/article_outline_generator/article_outline_generator.py print-schemas
```

**Expected Output**:
```json
{
  "input_schema": {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "properties": {
      "content": {"type": "string", "minLength": 1},
      "interim": {"type": "boolean", "default": false},
      "classification_method": {"enum": ["auto", "rules_only", "llm_preferred"]}
    }
  },
  "output_schema": {
    "properties": {
      "meta": {
        "properties": {
          "classification_confidence": {"type": "number", "minimum": 0.0, "maximum": 1.0},
          "classification_method": {"enum": ["rule_based", "llm_single", "llm_double"]}
        }
      }
    }
  },
  "envelope_schema": {
    "properties": {
      "meta": {
        "properties": {
          "classification_enhanced": {"type": "boolean"},
          "cost": {
            "properties": {
              "llm_calls": {"type": "integer", "maximum": 2}
            }
          }
        }
      }
    }
  }
}
```

**Success Criteria**:
- ✅ Valid JSON schemas generated
- ✅ Enhanced fields present in schemas
- ✅ Backward compatibility maintained
- ✅ Constitutional compliance verified

## Performance Validation

### Budget Compliance Check
```bash
# Test with large content to verify token budgets
echo '{
  "content": "'$(yes "This is test content. " | head -500 | tr -d '\n')'",
  "target_depth": 3
}' | timeout 10s python agents/article_outline_generator/article_outline_generator.py run
```

**Success Criteria**:
- ✅ Completes within 10s timeout
- ✅ Token usage ≤2000 per call
- ✅ Memory usage <100MB
- ✅ No performance degradation

### Concurrent Request Handling
```bash
# Test multiple parallel requests
for i in {1..5}; do (
  echo '{"content": "Test content '${i}'", "interim": true}' |
  python agents/article_outline_generator/article_outline_generator.py run &
); done
wait
```

**Success Criteria**:
- ✅ All requests complete successfully
- ✅ No resource conflicts
- ✅ Consistent performance across requests

## Definition of Done

All scenarios must pass with success criteria met:
- [ ] Backward compatibility preserved (Scenario 1)
- [ ] Enhanced classification working (Scenario 2)
- [ ] Interim classification functional (Scenario 3)
- [ ] Story classification enhanced (Scenario 4)
- [ ] Graceful degradation working (Scenario 5)
- [ ] Error handling proper (Scenario 6)
- [ ] Performance compliance verified (Scenario 7)
- [ ] Schema validation passing (Scenario 8)
- [ ] Budget compliance confirmed
- [ ] Concurrent handling verified

**Ready for Production**: All quickstart scenarios pass + constitutional compliance verified + performance budgets met

---
*Validation scenarios complete. Ready for implementation task generation.*
