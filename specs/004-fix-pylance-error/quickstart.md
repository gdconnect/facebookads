# Quickstart: Pydantic V1 to V2 Validator Migration

## Overview
Quick verification guide for the Pydantic validator migration from V1 to V2 syntax.

## Pre-Migration Verification

### 1. Check Current Warnings
```bash
# Open the file in VS Code or PyCharm and verify Pylance warnings
code brand_identity_generator.py
# Expected: Multiple deprecation warnings about @validator decorators
```

### 2. Baseline Test Run
```bash
# Run tests to establish baseline behavior
python -m pytest tests/contract/test_configuration_validation.py -v
# Expected: All tests should pass (some may be skipped as placeholders)
```

### 3. Manual Validation Test
```bash
# Test configuration validation manually
python -c "
from brand_identity_generator import DeveloperConfig
try:
    config = DeveloperConfig(llm_provider='invalid')
except ValueError as e:
    print('Error (expected):', e)
"
# Expected: Clear error message about invalid provider
```

## Post-Migration Verification

### 1. Verify No Warnings
```bash
# Check that Pylance warnings are gone
code brand_identity_generator.py
# Expected: No deprecation warnings about validators
```

### 2. Test Suite Verification
```bash
# Verify all tests still pass with identical behavior
python -m pytest tests/contract/test_configuration_validation.py -v
# Expected: Same test results as pre-migration
```

### 3. Configuration Loading Test
```bash
# Test configuration system works identically
python brand_identity_generator.py --help
# Expected: Help text shows with configuration defaults
```

### 4. Validation Behavior Test
```bash
# Test that validation still works with same error messages
python -c "
from brand_identity_generator import DeveloperConfig

# Test valid config
config = DeveloperConfig(llm_provider='anthropic')
print('Valid config:', config.llm_provider)

# Test invalid provider
try:
    DeveloperConfig(llm_provider='invalid')
except ValueError as e:
    print('Invalid provider error:', e)

# Test invalid timeout
try:
    DeveloperConfig(request_timeout=0.5)
except ValueError as e:
    print('Invalid timeout error:', e)

# Test invalid URL
try:
    DeveloperConfig(llm_base_url='invalid-url')
except ValueError as e:
    print('Invalid URL error:', e)
"
# Expected: Same error messages as before migration
```

### 5. CLI Validation Test
```bash
# Test CLI argument validation works identically
python brand_identity_generator.py /dev/null --enhance --llm-provider invalid 2>&1 | head -5
# Expected: Same error handling as before
```

### 6. Environment Variable Test
```bash
# Test environment variable validation
BRAND_TOOL_LLM_PROVIDER=invalid python -c "
from brand_identity_generator import DeveloperConfig
try:
    config = DeveloperConfig()
except ValueError as e:
    print('Env var validation error:', e)
"
# Expected: Environment variable validation works identically
```

## Performance Verification

### 1. Import Time Test
```bash
# Verify import time is not affected
python -c "
import time
start = time.time()
import brand_identity_generator
end = time.time()
print(f'Import time: {(end-start)*1000:.1f}ms')
"
# Expected: Similar import time to before migration
```

### 2. Validation Speed Test
```bash
# Test validation performance
python -c "
import time
from brand_identity_generator import DeveloperConfig

# Time multiple validations
start = time.time()
for i in range(1000):
    config = DeveloperConfig(llm_provider='openai')
end = time.time()
print(f'1000 validations: {(end-start)*1000:.1f}ms')
"
# Expected: No significant performance regression
```

## Success Criteria Checklist

### ✅ Pre-Migration Checklist
- [ ] Pylance shows deprecation warnings for @validator
- [ ] All existing tests pass
- [ ] Configuration validation works with clear error messages
- [ ] CLI help shows configuration defaults
- [ ] Manual validation testing produces expected errors

### ✅ Post-Migration Checklist
- [ ] No Pylance deprecation warnings about validators
- [ ] All tests pass with identical results
- [ ] Configuration validation works with identical error messages
- [ ] CLI help shows same configuration defaults
- [ ] Manual validation testing produces identical errors
- [ ] Environment variable validation unchanged
- [ ] Import time not significantly affected
- [ ] Validation performance not degraded

### ✅ Migration Quality Gates
- [ ] All functional requirements met (FR-001 through FR-007)
- [ ] Validator syntax updated to @field_validator
- [ ] @classmethod decorators added where required
- [ ] Import statements updated
- [ ] No behavior changes in validation logic
- [ ] Error messages remain identical
- [ ] Performance impact negligible

## Rollback Plan
If any verification step fails:

1. **Immediate Rollback**:
   ```bash
   git checkout HEAD~1 brand_identity_generator.py
   ```

2. **Verify Rollback**:
   ```bash
   python -m pytest tests/contract/ -x
   python brand_identity_generator.py --help
   ```

3. **Investigation**: Compare error outputs between versions
4. **Fix Forward**: Address specific issues found in verification

## Common Issues and Solutions

### Issue: Import Error
**Symptom**: `ImportError: cannot import name 'field_validator'`
**Solution**: Verify Pydantic V2 is installed: `pip show pydantic`

### Issue: Validation Behavior Changed
**Symptom**: Different error messages or validation logic
**Solution**: Check validator logic hasn't been accidentally modified

### Issue: Performance Regression
**Symptom**: Noticeably slower validation
**Solution**: Compare with baseline, check for unintended changes

### Issue: Tests Fail
**Symptom**: Previously passing tests now fail
**Solution**: Compare test outputs, ensure no logic changes occurred

## Final Verification
```bash
# Complete application test
echo "# Test Brand" > test.md
echo "Primary: blue" >> test.md
python brand_identity_generator.py test.md --enhance
rm test.md
# Expected: Application works end-to-end without warnings
```