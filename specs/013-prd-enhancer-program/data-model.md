# Data Model: PRD Enhancer Program

**Date**: 2025-09-23
**Feature**: 013-prd-enhancer-program

## Core Entities

### 1. PRD Document
**Description**: Input markdown file containing product requirements
- **file_path**: string (required) - Path to input PRD markdown file
- **content**: string - Raw markdown content
- **word_count**: integer - Total word count for processing decisions
- **created_at**: datetime - File creation timestamp

**Validation Rules**:
- file_path must be valid readable file
- content must be valid markdown format
- word_count >= 0

**State Transitions**:
- UNLOADED → LOADED → PARSED → ANALYZED

### 2. Enhanced PRD
**Description**: Output markdown file with improvements
- **content**: string (required) - Enhanced markdown content
- **complexity_score**: integer (0-100) - Implementation complexity rating
- **feature_count**: integer - Number of core features after reduction
- **page_count**: float - Estimated page length
- **processing_time**: float - Total processing time in seconds

**Validation Rules**:
- complexity_score between 0-100
- feature_count <= 5
- page_count <= 3.0
- processing_time <= 10.0

### 3. Ambiguity
**Description**: Vague term identified in PRD with suggested replacement
- **term**: string (required) - Original ambiguous term
- **context**: string - Surrounding text context
- **problem**: string (required) - Why the term is vague
- **suggested_fix**: string (required) - Specific metric replacement
- **confidence**: float (0.0-1.0) - Detection confidence score
- **source**: enum (llm|regex) - Detection method used

**Validation Rules**:
- term must not be empty
- confidence between 0.0 and 1.0
- source must be 'llm' or 'regex'

### 4. Feature
**Description**: Individual capability that can be prioritized
- **name**: string (required) - Feature name/title
- **description**: string - Detailed feature description
- **priority_score**: float - Value/effort ratio (ROI)
- **value_score**: integer (1-10) - Business value rating
- **effort_score**: integer (1-10) - Implementation effort rating
- **status**: enum (core|cut|not_doing) - Selection status
- **category**: string - Feature category/domain

**Validation Rules**:
- priority_score = value_score / effort_score
- value_score and effort_score between 1-10
- status must be valid enum value

### 5. Domain Event
**Description**: Workflow step extracted from PRD
- **name**: string (required) - Event name (PascalCase)
- **description**: string - Event description
- **trigger**: string - What triggers this event
- **outcome**: string - Expected outcome
- **sequence**: integer - Order in workflow (1-5)

**Validation Rules**:
- name must be PascalCase format
- sequence between 1-5
- Maximum 5 events per PRD

### 6. Complexity Score
**Description**: Numerical assessment of implementation difficulty
- **total_score**: integer (0-100) - Overall complexity
- **entities_count**: integer - Number of data entities
- **events_count**: integer - Number of domain events
- **integrations_count**: integer - Number of external integrations
- **formula**: string - Calculation formula used

**Validation Rules**:
- total_score = (entities_count * 3) + (events_count * 2) + (integrations_count * 5)
- All counts >= 0
- total_score between 0-100

### 7. JSON Schema
**Description**: Minimal data structure definition
- **entity_name**: string (required) - Name of the entity
- **schema**: dict (required) - JSON schema definition
- **required_fields**: list[string] - List of required field names
- **field_count**: integer - Total number of fields

**Validation Rules**:
- schema must be valid JSON schema format
- required_fields must be subset of schema properties
- Minimal schemas only (essential fields only)

## Relationships

### PRD Document → Features (1:many)
- One PRD contains multiple features
- Features extracted from PRD content
- Maximum 5 core features selected

### PRD Document → Ambiguities (1:many)
- One PRD may contain multiple ambiguous terms
- Maximum 10 ambiguities reported
- Each ambiguity has location context

### PRD Document → Domain Events (1:many)
- One PRD may describe multiple workflow events
- Maximum 5 events extracted
- Events represent happy path only

### Enhanced PRD → JSON Schemas (1:many)
- Enhanced PRD generates schemas for entities
- One schema per entity mentioned
- Minimal field sets only

### Features → Complexity Score (many:1)
- All features contribute to complexity calculation
- Score influences Pass 3 trigger (>50)

## Processing Pipeline

### Input Validation
1. Validate file_path exists and readable
2. Parse markdown content
3. Calculate word_count
4. Determine processing strategy based on size

### Analysis Pipeline
1. **Pass 1**: Extract ambiguities (always)
2. **Pass 2**: Analyze and prioritize features (if >7 features)
3. **Pass 3**: Check contradictions (if complexity >50)
4. Calculate final complexity score
5. Generate JSON schemas for entities

### Output Generation
1. Assemble enhanced PRD content
2. Ensure page count <= 3
3. Validate all business rules
4. Write output file with metadata

## Business Rules

### Feature Selection Rules
- Maximum 5 core features in output
- Feature priority_score > 2.0 to survive
- "Not doing" list must be 2x "doing" list size

### LLM Usage Rules
- Skip all passes if word_count < 500
- Skip Pass 2 if features <= 5
- Skip Pass 3 if complexity_score <= 30
- Use fallbacks if any pass times out

### Quality Gates
- Enhanced PRD must be shorter than original
- Complexity score must decrease by >30% for complex PRDs
- All ambiguities must have specific replacement suggestions
- Processing time must not exceed 10 seconds