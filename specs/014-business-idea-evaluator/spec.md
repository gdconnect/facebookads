# Feature Specification: Business Idea Evaluator (BIE)

**Feature Branch**: `014-business-idea-evaluator`
**Created**: 2025-09-24
**Status**: Draft
**Input**: User description: "business_idea_evaluator please read @docs/business_idea_evaluator.md and specify it for development"

## Execution Flow (main)
```
1. Parse user description from Input
   ’ If empty: ERROR "No feature description provided"
2. Extract key concepts from description
   ’ Identified: business idea evaluation, markdown processing, LLM integration, scoring system
3. For each unclear aspect:
   ’ All requirements derived from comprehensive PRD documentation
4. Fill User Scenarios & Testing section
   ’ Clear user flow: markdown input ’ multi-pass evaluation ’ structured output
5. Generate Functional Requirements
   ’ Each requirement testable and measurable
6. Identify Key Entities (business ideas, evaluation schemas, scores)
7. Run Review Checklist
   ’ No ambiguities requiring clarification
   ’ Focus maintained on user value
8. Return: SUCCESS (spec ready for planning)
```

---

## ¡ Quick Guidelines
-  Focus on WHAT users need and WHY
- L Avoid HOW to implement (no tech stack, APIs, code structure)
- =e Written for business stakeholders, not developers

---

## User Scenarios & Testing *(mandatory)*

### Primary User Story
A web development agency developer has a business idea written in markdown format and wants to systematically evaluate its viability before investing development resources. They run the Business Idea Evaluator tool, which transforms their unstructured idea into a comprehensive evaluation with actionable insights, helping them make data-driven decisions about whether to pursue the opportunity.

### Acceptance Scenarios
1. **Given** a markdown file containing a business idea description, **When** the user runs the evaluation command, **Then** the system outputs a comprehensive evaluation with scalability, complexity, and risk scores along with specific recommendations
2. **Given** multiple business idea files, **When** the user runs the comparison command, **Then** the system provides a ranked comparison showing which ideas have the highest potential
3. **Given** an incomplete or vague business idea description, **When** the evaluation runs, **Then** the system identifies specific gaps and asks critical questions that must be answered before proceeding
4. **Given** a completed evaluation, **When** the user requests enhanced markdown output, **Then** the system provides an annotated version of their original idea with refinements and next steps

### Edge Cases
- What happens when the input markdown file is empty or contains no recognizable business idea structure?
- How does the system handle evaluation timeouts or LLM API failures during processing?
- What occurs when the scoring algorithm produces edge case results (all zeros, conflicting metrics)?
- How does the system respond to malformed markdown or unexpected file formats?

## Requirements *(mandatory)*

### Functional Requirements
- **FR-001**: System MUST accept markdown files containing business idea descriptions as input
- **FR-002**: System MUST extract explicit business idea components (problem, solution, target customer, monetization) from markdown text
- **FR-003**: System MUST perform multi-pass LLM-based enrichment to analyze business model, scalability factors, and risks
- **FR-004**: System MUST calculate quantitative scores for scalability (0-100), complexity (0-100, lower better), and risk (0-100, lower better)
- **FR-005**: System MUST generate an overall grade (A-F) based on the computed scores using defined thresholds
- **FR-006**: System MUST produce actionable insights including critical questions, quick wins, red flags, and next steps
- **FR-007**: System MUST support multiple output formats (JSON and enhanced markdown)
- **FR-008**: System MUST complete full evaluation in under 2 minutes end-to-end
- **FR-009**: System MUST detect and flag common agency development blindspots (features over distribution, technical bias, etc.)
- **FR-010**: System MUST provide comparison functionality for evaluating multiple business ideas simultaneously
- **FR-011**: System MUST handle LLM API failures gracefully with retry logic and fallback messaging
- **FR-012**: System MUST validate all scoring calculations and provide evidence for recommendations
- **FR-013**: System MUST generate recommended MVP scope that can be built within 30 days
- **FR-014**: System MUST identify similar successful companies that proved the business model

### Key Entities *(include if feature involves data)*
- **RawIdea**: Represents the initial business idea extraction with name, problem, solution, target customer, monetization approach, technical approach, and inspiration
- **BusinessModel**: Represents refined business mechanics including value creation, value capture, unit economics, growth mechanisms, competitive advantages, and minimum viable scope
- **ScalabilityFactors**: Represents growth potential analysis including marginal costs, geographic constraints, automation potential, network effects, platform potential, and data advantages
- **RiskAssessment**: Represents reality check analysis including startup costs, time to revenue, key dependencies, biggest risks, simplified versions, and market gap explanations
- **EvaluatedIdea**: Represents the complete evaluated business idea combining all analysis components with computed scores, grades, and actionable recommendations

---

## Review & Acceptance Checklist
*GATE: Automated checks run during main() execution*

### Content Quality
- [x] No implementation details (languages, frameworks, APIs)
- [x] Focused on user value and business needs
- [x] Written for non-technical stakeholders
- [x] All mandatory sections completed

### Requirement Completeness
- [x] No [NEEDS CLARIFICATION] markers remain
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
- [x] Review checklist passed

---