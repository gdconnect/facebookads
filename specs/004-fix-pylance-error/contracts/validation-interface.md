# Validation Interface Contract

## Overview
Contract defining the validation behavior that must be preserved during Pydantic V1 to V2 migration.

## Validation Contract

### Input/Output Specification
```python
# Validator Function Contract
def validator_function(cls, value: Any) -> Any:
    """
    Input: Raw field value from user/config/environment
    Output: Validated and possibly transformed value
    Raises: ValueError with descriptive message for invalid inputs
    """
```

### Error Message Contract
```python
# Error Format Contract
class ValidationErrorContract:
    """
    Error messages must remain identical before and after migration
    """
    field_name: str  # Field that failed validation
    error_message: str  # Human-readable error description
    input_value: Any  # Value that caused the error
    suggested_values: Optional[List[str]]  # Valid alternatives if applicable
```

### Specific Validator Contracts

#### LLM Provider Validation
```python
def validate_llm_provider(cls, value: str) -> str:
    """
    Contract: Must validate provider against allowed list
    Valid: 'openai', 'anthropic', 'local'
    Invalid: Any other string
    Error Format: "Invalid LLM provider '{value}'. Valid options: openai, anthropic, local"
    """
```

#### URL Validation
```python
def validate_base_url(cls, value: Optional[str]) -> Optional[str]:
    """
    Contract: Must validate URL format if provided
    Valid: None, 'http://example.com', 'https://example.com'
    Invalid: 'ftp://example.com', 'example.com', 'invalid-url'
    Error Format: "Invalid base URL format '{value}'. Must start with http:// or https://"
    """
```

#### Timeout Validation
```python
def validate_timeout(cls, value: float) -> float:
    """
    Contract: Must validate timeout is positive and reasonable
    Valid: 1.0, 30.0, 300.0
    Invalid: 0.0, -1.0, 0.5
    Error Format: "Request timeout must be >= 1.0 seconds, got {value}"
    """
```

#### Retry Count Validation
```python
def validate_max_retries(cls, value: int) -> int:
    """
    Contract: Must validate retry count within bounds
    Valid: 0, 3, 10
    Invalid: -1, 11, 100
    Error Format: "Max retries must be between 0 and 10, got {value}"
    """
```

#### Backoff Factor Validation
```python
def validate_backoff_factor(cls, value: float) -> float:
    """
    Contract: Must validate backoff multiplier within reasonable range
    Valid: 1.0, 2.0, 5.0
    Invalid: 0.5, 10.0, -1.0
    Error Format: "Retry backoff factor must be between 1.0 and 5.0, got {value}"
    """
```

#### Enhancement Level Validation
```python
def validate_enhancement_level(cls, value: str) -> str:
    """
    Contract: Must validate enhancement level against allowed options
    Valid: 'minimal', 'moderate', 'comprehensive'
    Invalid: 'high', 'low', 'maximum'
    Error Format: "Invalid enhancement level '{value}'. Valid options: minimal, moderate, comprehensive"
    """
```

#### Log Level Validation
```python
def validate_log_level(cls, value: str) -> str:
    """
    Contract: Must validate log level against Python logging levels
    Valid: 'DEBUG', 'INFO', 'WARNING', 'ERROR'
    Invalid: 'TRACE', 'debug', 'info'
    Error Format: "Invalid log level '{value}'. Valid options: DEBUG, INFO, WARNING, ERROR"
    """
```

## Migration Verification Contract

### Before/After Comparison
```python
class MigrationContract:
    """
    Contract for verifying identical behavior before/after migration
    """

    def test_identical_validation(self, test_cases: List[TestCase]):
        """
        For each test case:
        1. Run with V1 validators (before migration)
        2. Run with V2 validators (after migration)
        3. Assert identical results (value or exception)
        4. Assert identical error messages if validation fails
        """

    def test_performance_parity(self):
        """
        Verify validation performance is identical or better
        """

    def test_error_message_format(self):
        """
        Verify error message format and content unchanged
        """
```

### Test Case Coverage
```python
# Required test cases for each validator
test_cases = [
    # Valid inputs
    {"input": valid_value, "expected": valid_value},

    # Invalid inputs
    {"input": invalid_value, "expected": ValueError("specific message")},

    # Edge cases
    {"input": boundary_value, "expected": boundary_result},

    # Type coercion
    {"input": coercible_value, "expected": coerced_value},
]
```

## Success Criteria

### Functional Requirements
1. **Identical Validation Logic**: All validation rules work exactly as before
2. **Identical Error Messages**: Error text, format, and details unchanged
3. **Identical Performance**: No measurable performance difference
4. **Zero Deprecation Warnings**: Pylance shows no validator-related warnings

### Quality Requirements
1. **Full Test Coverage**: All validator scenarios tested
2. **Regression Prevention**: Existing test suite passes unchanged
3. **Documentation Accuracy**: Any validator documentation remains accurate
4. **Code Quality**: Follows Pydantic V2 best practices

### Acceptance Criteria
1. All existing tests pass without modification
2. IDE shows no deprecation warnings
3. Manual testing shows identical behavior
4. Performance benchmarks show no regression