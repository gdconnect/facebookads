# Pydantic V1 to V2 Migration Baseline Documentation

## Current Pylance Warnings

### Deprecation Warnings for @validator Decorators

The following Pylance deprecation warnings are currently present in `brand_identity_generator.py`:

#### DeveloperConfig Class Validators (Lines 54-97)
1. **Line 54**: `@validator('llm_provider')`
   - Warning: `@validator` is deprecated in Pydantic V2
   - Function: `validate_llm_provider`

2. **Line 61**: `@validator('llm_base_url')`
   - Warning: `@validator` is deprecated in Pydantic V2
   - Function: `validate_base_url`

3. **Line 67**: `@validator('request_timeout')`
   - Warning: `@validator` is deprecated in Pydantic V2
   - Function: `validate_timeout`

4. **Line 73**: `@validator('max_retries')`
   - Warning: `@validator` is deprecated in Pydantic V2
   - Function: `validate_max_retries`

5. **Line 79**: `@validator('retry_backoff_factor')`
   - Warning: `@validator` is deprecated in Pydantic V2
   - Function: `validate_backoff_factor`

6. **Line 85**: `@validator('default_enhancement_level')`
   - Warning: `@validator` is deprecated in Pydantic V2
   - Function: `validate_enhancement_level`

7. **Line 92**: `@validator('log_level')`
   - Warning: `@validator` is deprecated in Pydantic V2
   - Function: `validate_log_level`

#### LLMResponse Class Validator (Line 351)
8. **Line 351**: `@validator('confidence_score')`
   - Warning: `@validator` is deprecated in Pydantic V2
   - Function: `validate_confidence`

#### GapItem Class Validator (Line 569)
9. **Line 569**: `@validator('impact')`
   - Warning: `@validator` is deprecated in Pydantic V2
   - Function: `validate_impact`

## Migration Target

All 9 validators need to be migrated from:
```python
@validator('field_name')
def validate_field(cls, v):
    # validation logic
    return v
```

To Pydantic V2 syntax:
```python
@field_validator('field_name')
@classmethod
def validate_field(cls, v):
    # validation logic (unchanged)
    return v
```

## Current Import Status

The file already imports both decorators:
```python
from pydantic import BaseModel, Field, field_validator, validator
```

After migration, the `validator` import can be removed.

## Validation Behavior to Preserve

### DeveloperConfig Validators
- `llm_provider`: Must be one of ["openai", "anthropic", "local"]
- `llm_base_url`: Must start with "http://" or "https://" if not None
- `request_timeout`: Must be >= 1.0 seconds
- `max_retries`: Must be between 0 and 10
- `retry_backoff_factor`: Must be between 1.0 and 5.0
- `default_enhancement_level`: Must be one of ["minimal", "moderate", "comprehensive"]
- `log_level`: Must be one of ["DEBUG", "INFO", "WARNING", "ERROR"]

### LLMResponse Validator
- `confidence_score`: Clamps values to 0.0-1.0 range (allows out-of-range input, normalizes to valid range)

### GapItem Validator
- `impact`: Must be one of ["low", "medium", "high", "critical"]

## Success Criteria

✅ **Pre-Migration State**:
- 9 Pylance deprecation warnings visible
- All validators functioning correctly
- Error messages clear and specific

✅ **Post-Migration Target**:
- 0 Pylance deprecation warnings
- Identical validation behavior
- Same error messages
- Same performance characteristics

## Test Coverage

Comprehensive baseline tests created in:
`tests/contract/test_pydantic_migration_baseline.py`

These tests capture:
- Valid input handling for all validators
- Invalid input error messages (exact text)
- Edge cases and boundary conditions
- Multiple validation error scenarios
- Default value behavior