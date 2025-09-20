# Data Model: Pydantic Validator Migration

## Overview
This feature involves migrating validation decorators without changing any data structures. The data model remains identical - only the validation syntax changes.

## Affected Entities

### Validator Functions
**Description**: Methods that validate field values in Pydantic models
**Current State**: Using deprecated `@validator` syntax
**Target State**: Using current `@field_validator` syntax

**Attributes**:
- Field name being validated
- Validation logic (unchanged)
- Error messages (unchanged)
- Return value processing (unchanged)

**Relationships**:
- Belongs to: Pydantic model classes
- Validates: Model field values
- Returns: Validated/transformed values

### Configuration Classes
**Description**: Pydantic models that use validation decorators
**Affected Classes**:
- `DeveloperConfig`: Primary configuration model
- `LLMRequest`: Request validation model
- `LLMResponse`: Response validation model
- `ResolvedConfig`: Runtime configuration model

**Changes**:
- Decorator syntax only
- Field definitions unchanged
- Validation logic unchanged
- Error handling unchanged

### Error Messages
**Description**: Validation error messages shown to users
**Requirement**: Must remain identical after migration
**Format**: ValidationError with field-specific messages
**Content**: Same error text, suggestions, and formatting

## Validation Rules (Unchanged)

### DeveloperConfig Validators
1. **llm_provider**: Must be in ['openai', 'anthropic', 'local']
2. **llm_base_url**: Must start with 'http://' or 'https://' if provided
3. **request_timeout**: Must be >= 1.0 seconds
4. **max_retries**: Must be between 0 and 10
5. **retry_backoff_factor**: Must be between 1.0 and 5.0
6. **default_enhancement_level**: Must be in ['minimal', 'moderate', 'comprehensive']
7. **log_level**: Must be in ['DEBUG', 'INFO', 'WARNING', 'ERROR']

### LLMRequest Validators
1. **confidence_score**: Must be between 0.0 and 1.0

### Other Model Validators
1. **impact**: Must be in predefined impact levels
2. Additional validators as found in codebase

## State Transitions
**None** - This is a code quality improvement with no state changes.

## Validation Flow (Unchanged)
1. User provides configuration values
2. Pydantic validates each field using validators
3. Invalid values trigger ValidationError with specific messages
4. Valid values are processed and stored in model

## Migration Mapping

### Syntax Changes Only
```python
# Before (V1 - deprecated)
@validator('field_name')
def validate_field(cls, v):
    # validation logic
    return v

# After (V2 - current)
@field_validator('field_name')
@classmethod
def validate_field(cls, v):
    # identical validation logic
    return v
```

### No Data Structure Changes
- Model field definitions remain identical
- Field types remain identical
- Default values remain identical
- Field constraints remain identical
- Documentation strings remain identical

## Testing Requirements

### Validation Behavior Tests
1. **Input/Output Mapping**: Same inputs produce same outputs
2. **Error Messages**: Identical error text and formatting
3. **Edge Cases**: Same handling of boundary conditions
4. **Type Coercion**: Same type conversion behavior

### Regression Tests
1. **Configuration Loading**: All config scenarios work identically
2. **CLI Processing**: Command-line validation unchanged
3. **Error Handling**: Error propagation and formatting unchanged
4. **Performance**: No measurable performance difference

## Dependencies
- **Pydantic V2**: Already installed and in use
- **Python Type System**: No changes needed
- **Import Statements**: Add `field_validator` import

## Backward Compatibility
**Full Compatibility**: All existing functionality works identically after migration.

## Performance Impact
**None Expected**: Validator execution path identical in Pydantic V2 for both syntaxes during transition period.