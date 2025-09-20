# Data Model: Constitutional Compliance Validation

## Core Entities

### ValidationReport
**Purpose**: Main output structure containing all compliance assessment results
**Attributes**:
- `validation_id`: Unique identifier for this validation run
- `target_file`: Path to the file being validated (customer_journey_mapper.py)
- `constitution_version`: Version of constitution used (v1.3.5)
- `timestamp`: ISO-8601 timestamp of validation execution
- `overall_status`: PASS/FAIL/WARNING overall compliance status
- `article_results`: List of ArticleAssessment objects
- `summary_stats`: ValidationSummary object
- `remediation_guidance`: List of remediation recommendations

**Validation Rules**:
- validation_id must be UUID format
- target_file must exist and be readable
- constitution_version must match expected version
- article_results must contain exactly 17 assessments (Articles I-XVII)

### ArticleAssessment
**Purpose**: Compliance assessment result for a single constitutional article
**Attributes**:
- `article_number`: Roman numeral (I-XVII)
- `article_title`: Human-readable article name
- `status`: PASS/FAIL/WARNING/SKIP compliance status
- `checks_performed`: List of CheckResult objects
- `violations`: List of violation descriptions (if any)
- `score`: Numeric score for quantifiable metrics (0.0-1.0)
- `execution_time_ms`: Time taken to validate this article

**Validation Rules**:
- article_number must be valid Roman numeral I-XVII
- status must be from allowed enum values
- score must be between 0.0 and 1.0 (1.0 = perfect compliance)
- violations list must be empty when status is PASS

### CheckResult
**Purpose**: Result of a specific validation check within an article
**Attributes**:
- `check_name`: Identifier for the specific check performed
- `tool_used`: Static analysis tool or validation method used
- `status`: PASS/FAIL/WARNING/ERROR status
- `details`: Human-readable description of check result
- `evidence`: Supporting data (file paths, line numbers, tool output)
- `execution_time_ms`: Time taken for this specific check

**Validation Rules**:
- check_name must be non-empty string
- tool_used must be from approved tool list or "internal"
- evidence must be structured data (dict/list) for programmatic access

### ValidationSummary
**Purpose**: High-level statistics and metrics for the validation run
**Attributes**:
- `total_articles`: Total number of articles validated (17)
- `passed_articles`: Count of articles with PASS status
- `failed_articles`: Count of articles with FAIL status
- `warning_articles`: Count of articles with WARNING status
- `overall_score`: Weighted average score across all articles (0.0-1.0)
- `execution_time_total_ms`: Total time for entire validation
- `tools_used`: List of external tools successfully executed

**Validation Rules**:
- total_articles must equal 17
- passed_articles + failed_articles + warning_articles must equal total_articles
- overall_score calculation must be documented and consistent

### ConstitutionalArticle
**Purpose**: Reference data structure defining each constitutional article
**Attributes**:
- `number`: Roman numeral identifier (I-XVII)
- `title`: Full article title
- `description`: Brief description of article requirements
- `validation_methods`: List of validation approaches for this article
- `required_tools`: External tools needed for validation
- `pass_criteria`: Specific criteria that must be met for PASS status
- `weight`: Importance weight for overall score calculation (0.1-1.0)

**Validation Rules**:
- number must be unique across all articles
- validation_methods must be non-empty list
- weight must sum to reasonable total across all articles

### ValidationConfig
**Purpose**: Configuration settings for the validation process
**Attributes**:
- `target_file_path`: Absolute path to file being validated
- `constitution_path`: Path to constitution.md file
- `tool_paths`: Dictionary mapping tool names to executable paths
- `timeout_seconds`: Maximum time allowed for validation (default: 30)
- `parallel_execution`: Enable parallel tool execution (default: true)
- `strict_mode`: Fail on warnings (default: false)
- `output_format`: Report output format (json/yaml/text)

**Validation Rules**:
- target_file_path must be absolute path to existing Python file
- timeout_seconds must be positive integer
- tool_paths must contain paths to required static analysis tools

## Entity Relationships

### Primary Relationships
- `ValidationReport` contains multiple `ArticleAssessment` objects (1:N)
- `ArticleAssessment` contains multiple `CheckResult` objects (1:N)
- `ValidationReport` contains one `ValidationSummary` object (1:1)
- `ConstitutionalArticle` templates used to generate `ArticleAssessment` (1:1)

### Data Flow
1. `ValidationConfig` → Validation Engine initialization
2. `ConstitutionalArticle` definitions → Validation rule setup
3. Validation execution → Multiple `CheckResult` objects
4. `CheckResult` aggregation → `ArticleAssessment` objects
5. `ArticleAssessment` compilation → `ValidationReport` with `ValidationSummary`

## State Transitions

### Validation Process States
- **INITIALIZED**: Configuration loaded, ready to start validation
- **RUNNING**: Validation checks in progress
- **COMPLETED**: All validations finished successfully
- **FAILED**: Validation process encountered fatal error
- **TIMEOUT**: Validation exceeded time limit

### Article Assessment States
- **PENDING**: Article validation not yet started
- **IN_PROGRESS**: Article validation currently running
- **PASS**: Article fully compliant with constitution
- **FAIL**: Article has compliance violations that must be fixed
- **WARNING**: Article has minor issues or potential improvements
- **SKIP**: Article validation skipped (missing dependencies)
- **ERROR**: Article validation failed due to technical error

## Validation Constraints

### Data Integrity
- All entities must have complete required attributes
- Foreign key relationships must be valid (article numbers, check names)
- Enumerated values must be from approved lists
- Numeric scores and times must be non-negative

### Performance Constraints
- Individual check execution must complete within reasonable time (<10s)
- Total validation report size should be <1MB for reasonable performance
- Memory usage should not exceed 100MB during validation process

### Constitutional Compliance
- Data model itself must follow constitutional principles
- All entities must be serializable to JSON for Agent Envelope output
- Validation logic must use decision tables (Article III)
- Type safety must be enforced with full type hints (Article VII)