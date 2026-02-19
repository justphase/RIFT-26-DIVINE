# PGx AI Analyzer

AI-powered pharmacogenomic analysis application based on CPIC guidelines. Analyzes VCF files and drug names to predict personalized pharmacogenomic risks.

## Features

- **VCF Parsing**: Extract RSIDs and genotypes from uploaded .vcf files
- **Risk Engine**: Map diplotypes to phenotypes (PM, IM, NM, RM, URM) and then to risk labels (Safe, Adjust Dosage, Toxic, Ineffective)
- **6 Critical Genes**: CYP2D6, CYP2C19, CYP2C9, SLCO1B1, TPMT, DPYD
- **Smart Patient Guidance**: AI-powered personalized medication recommendations and Doctor Discussion Card
- **Modern UI**: React + Tailwind CSS with clinical-grade design
- **Download JSON**: Export analysis results

## Tech Stack

- **Frontend**: React.js + Tailwind CSS
- **Backend**: FastAPI (Python)
- **VCF Parsing**: Custom parser with cyvcf2 fallback
- **AI Engine**: OpenAI integration with fallback mode

## Supported Drugs & Genes

| Gene | Drugs |
|------|-------|
| CYP2D6 | Codeine, Tramadol, Metoprolol |
| CYP2C19 | Clopidogrel, Omeprazole, Lansoprazole |
| CYP2C9 | Warfarin, Losartan, Phenytoin |
| SLCO1B1 | Simvastatin, Atorvastatin, Rosuvastatin |
| TPMT | Azathioprine, Mercaptopurine, Thioguanine |
| DPYD | Fluorouracil, Capecitabine, Tegafur |

## Installation

### Prerequisites

- Python 3.8+
- Node.js 16+
- npm or yarn

### Backend Setup

```
bash
cd backend

# Create virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start the backend server
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

### Frontend Setup

```
bash
cd frontend

# Install dependencies
npm install

# Start the development server
npm start
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API information |
| `/health` | GET | Health check |
| `/supported-drugs` | GET | List supported drugs |
| `/supported-genes` | GET | List supported genes |
| `/drug-info/{drug}` | GET | Get drug information |
| `/analyze` | POST | Analyze VCF file (multipart/form-data) |
| `/analyze/json` | POST | Analyze VCF content (JSON) |

## Usage

1. Start the backend server on port 8000
2. Start the frontend development server (usually on port 3000)
3. Open the frontend in your browser
4. Upload a VCF file or use one of the sample files
5. Select a drug to analyze
6. Click "Analyze Pharmacogenomic Risk"
7. View the results and download as JSON

### Sample VCF Files

Three sample VCF files are included in the `data/` folder:

- `safe_result.vcf` - Normal metabolizer (Safe result)
- `toxic_result.vcf` - Poor metabolizer (Toxic/Ineffective result)
- `adjust_dosage_result.vcf` - Intermediate metabolizer (Adjust Dosage result)

## Environment Variables

### Backend

- `OPENAI_API_KEY`: OpenAI API key for enhanced AI explanations (optional)
- `PORT`: Server port (default: 8000)

### Frontend

- `REACT_APP_API_URL`: Backend API URL (default: http://localhost:8000)

## Output Schema

```
json
{
  "patient_id": "PATIENT_XXX",
  "drug": "DRUG_NAME",
  "timestamp": "ISO8601_timestamp",
  "risk_assessment": {
    "risk_label": "Safe|Adjust Dosage|Toxic|Ineffective",
    "confidence_score": 0.0,
    "severity": "none|low|moderate|high|critical"
  },
  "pharmacogenomic_profile": {
    "primary_gene": "GENE_SYMBOL",
    "diplotype": "*X/*Y",
    "phenotype": "PM|IM|NM|RM|URM|Unknown",
    "detected_variants": [{ "rsid": "rsXXXX", "genotype": "AA/GG" }]
  },
  "clinical_recommendation": {
    "action": "Dose Reduction / Alternative Drug",
    "alternative_suggestion": "NAME_OF_BETTER_DRUG",
    "cpic_guideline_link": "URL"
  },
  "patient_advice": {
    "patient_friendly_summary": "Simple language explanation",
    "best_medicine_suggestion": "Alternative drug name and why it is safer for you",
    "doctor_talking_points": ["Point 1", "Point 2"]
  },
  "llm_generated_explanation": {
    "summary": "Biological mechanism explanation with variant citations"
  },
  "smart_patient_guidance": {
    "doctor_discussion_card": {
      "card_title": "Title",
      "card_content": "Content"
    }
  },
  "quality_metrics": { "vcf_parsing_success": true }
}
```

## CPIC Guidelines

This application is based on CPIC (Clinical Pharmacogenetics Implementation Consortium) guidelines. For more information, visit https://cpicpgx.org/

## Disclaimer

This application is for educational and research purposes only. The results should be validated by a qualified healthcare professional before making any clinical decisions.

## License

MIT License
