# PGx AI Analyzer - Project TODO

## Phase 1: Backend Setup
- [x] Create /backend directory structure
- [x] Create requirements.txt with dependencies
- [x] Create CPIC guidelines mapping (6 genes, drugs, diplotypes, phenotypes, risk labels)
- [x] Create VCF parser module (cyvcf2 with fallback)
- [x] Create risk engine module
- [x] Create LLM service (OpenAI with fallback mode)
- [x] Create FastAPI main application with /analyze endpoint

## Phase 2: Frontend Setup
- [x] Create /frontend React project with Tailwind CSS
- [x] Create main App component with clinical dashboard layout
- [x] Create VCF upload component with drag-and-drop
- [x] Create drug selection component
- [x] Create risk result cards (color-coded)
- [x] Create Smart Patient Guidance section
- [x] Create JSON download functionality

## Phase 3: Data & Testing
- [x] Create sample VCF file: safe_result.vcf (Normal metabolizer)
- [x] Create sample VCF file: toxic_result.vcf (Poor metabolizer)
- [x] Create sample VCF file: adjust_dosage_result.vcf (Intermediate metabolizer)

## Phase 4: Documentation
- [x] Create README.md with setup instructions

## Implementation Status:
- [x] Backend - FastAPI setup
- [x] Backend - CPIC Guidelines (6 genes)
- [x] Backend - VCF Parser
- [x] Backend - Risk Engine
- [x] Backend - LLM Service with fallback
- [x] Frontend - React + Tailwind setup
- [x] Frontend - Upload & Results UI
- [x] Frontend - Smart Patient Guidance
- [x] Data - Sample VCF files
