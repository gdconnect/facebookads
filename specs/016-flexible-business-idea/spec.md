# Feature Specification: Flexible Business Idea Generator

**Feature Branch**: `016-flexible-business-idea`
**Created**: 2025-09-24
**Status**: Draft
**Input**: User description: "flexible business idea generator - please allow the markdown documents to take different shapes, use LLM to coerce into the json shape required. agents/bie/bie.py"

## Execution Flow (main)
```
1. Parse user description from Input
   � If empty: ERROR "No feature description provided"
2. Extract key concepts from description
   � Identify: actors (users), actions (generate, evaluate), data (business ideas, markdown), constraints (flexible format)
3. For each unclear aspect:
   � Mark with [NEEDS CLARIFICATION: specific question]
4. Fill User Scenarios & Testing section
   � If no clear user flow: ERROR "Cannot determine user scenarios"
5. Generate Functional Requirements
   � Each requirement must be testable
   � Mark ambiguous requirements
6. Identify Key Entities (if data involved)
7. Run Review Checklist
   � If any [NEEDS CLARIFICATION]: WARN "Spec has uncertainties"
   � If implementation details found: ERROR "Remove tech details"
8. Return: SUCCESS (spec ready for planning)
```

---

## � Quick Guidelines
-  Focus on WHAT users need and WHY
- L Avoid HOW to implement (no tech stack, APIs, code structure)
- =e Written for business stakeholders, not developers

### Section Requirements
- **Mandatory sections**: Must be completed for every feature
- **Optional sections**: Include only when relevant to the feature
- When a section doesn't apply, remove it entirely (don't leave as "N/A")

### For AI Generation
When creating this spec from a user prompt:
1. **Mark all ambiguities**: Use [NEEDS CLARIFICATION: specific question] for any assumption you'd need to make
2. **Don't guess**: If the prompt doesn't specify something (e.g., "login system" without auth method), mark it
3. **Think like a tester**: Every vague requirement should fail the "testable and unambiguous" checklist item
4. **Common underspecified areas**:
   - User types and permissions
   - Data retention/deletion policies
   - Performance targets and scale
   - Error handling behaviors
   - Integration requirements
   - Security/compliance needs

---

## User Scenarios & Testing *(mandatory)*

### Primary User Story
As a business analyst or entrepreneur, I want to submit business ideas in various markdown formats (different structures, section names, and content organization) and have the system successfully extract and evaluate the core business components without requiring a strict template, so that I can focus on articulating my idea naturally rather than conforming to rigid formatting requirements.

### Acceptance Scenarios
1. **Given** a markdown file with sections named "Identifying the Problem" instead of "Problem", **When** the user submits it for evaluation, **Then** the system correctly identifies and extracts the problem statement
2. **Given** a markdown document with nested subsections and varied formatting, **When** processed, **Then** the system extracts all required business components (name, problem, solution) regardless of structure
3. **Given** a markdown file missing optional sections, **When** evaluated, **Then** the system processes successfully with available information
4. **Given** a markdown with alternative section names (e.g., "Revenue Model" vs "Monetization"), **When** analyzed, **Then** the system correctly maps content to appropriate fields

### Edge Cases
- What happens when required fields (problem, solution) are missing entirely?
- How does system handle markdown with no section headers at all?
- What occurs when content exceeds field length limits?
- How does system handle ambiguous section mappings?
- What happens with non-English content or special characters?

## Requirements *(mandatory)*

### Functional Requirements
- **FR-001**: System MUST accept markdown documents with varied structures and section naming conventions
- **FR-002**: System MUST intelligently extract business idea components (name, problem, solution) from flexible markdown formats
- **FR-003**: System MUST provide fallback extraction when exact section headers are not found
- **FR-004**: System MUST validate that minimum required fields (problem with 10+ chars, solution with 10+ chars) are present
- **FR-005**: System MUST handle optional fields (target customer, monetization, technical approach, inspiration) gracefully when missing
- **FR-006**: System MUST map alternative section names to standard fields (e.g., "Revenue Model" � "monetization")
- **FR-007**: System MUST preserve content meaning during extraction regardless of markdown structure
- **FR-008**: System MUST provide clear error messages when required content cannot be extracted
- **FR-009**: System MUST enforce field length limits . Have generous limits to fit most realistic business plans or ideas.
- **FR-010**: System MUST handle markdown files up to 2000 lines

### Key Entities *(include if feature involves data)*
- **Business Idea Document**: Represents the input markdown file containing business concept description with variable structure
- **Raw Idea**: Extracted business concept with standard fields (name, problem, solution, target_customer, monetization, technical_approach, inspiration)
- **Section Mapping**: Rules for matching various section names to standard fields
- **Extraction Result**: Success/failure status with extracted data or error details

---

## Review & Acceptance Checklist
*GATE: Automated checks run during main() execution*

### Content Quality
- [x] No implementation details (languages, frameworks, APIs)
- [x] Focused on user value and business needs
- [x] Written for non-technical stakeholders
- [x] All mandatory sections completed

### Requirement Completeness
- [ ] No [NEEDS CLARIFICATION] markers remain
- [x] Requirements are testable and unambiguous
- [x] Success criteria are measurable
- [x] Scope is clearly bounded
- [x] Dependencies and assumptions identified

---

## Execution Status
*Updated by main() during processing*

- [x] User description parsed
- [x] Key concepts extracted
- [x] Ambiguities marked
- [x] User scenarios defined
- [x] Requirements generated
- [x] Entities identified
- [ ] Review checklist passed (2 clarifications needed)

---
