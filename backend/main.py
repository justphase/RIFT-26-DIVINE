"""
FastAPI Main Application for PGx AI Analyzer
Provides REST API for pharmacogenomic analysis
"""

import os
import gzip
from typing import Optional
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# Import our modules
from risk_engine import RiskEngine
from llm_service import LLMService
from cpic_guidelines import get_supported_drugs, get_supported_genes

# Initialize FastAPI app
app = FastAPI(
    title="PGx AI Analyzer API",
    description="AI-powered pharmacogenomic analysis based on CPIC guidelines",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
risk_engine = RiskEngine()
llm_service = LLMService()

# Request models
class AnalyzeRequest(BaseModel):
    """Request model for analysis endpoint."""
    vcf_content: str
    drug: str
    patient_id: Optional[str] = "PATIENT_001"
    use_llm: bool = True

def _looks_like_vcf(content: str) -> bool:
    """Basic VCF signature check."""
    normalized = content.lstrip("\ufeff").strip()
    return "##fileformat=VCF" in normalized or "\n#CHROM" in normalized or normalized.startswith("#CHROM")

def _decode_vcf_upload(vcf_file: UploadFile, file_bytes: bytes) -> str:
    """Decode plain .vcf and compressed .vcf.gz uploads safely."""
    if not file_bytes:
        raise HTTPException(status_code=400, detail="Empty VCF file")

    filename = (vcf_file.filename or "").lower()
    is_gzip = filename.endswith(".gz") or file_bytes[:2] == b"\x1f\x8b"

    if is_gzip:
        try:
            file_bytes = gzip.decompress(file_bytes)
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid .vcf.gz file")

    for encoding in ("utf-8-sig", "utf-8"):
        try:
            return file_bytes.decode(encoding)
        except UnicodeDecodeError:
            continue

    raise HTTPException(status_code=400, detail="VCF file must be UTF-8 encoded text")

# Routes

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "PGx AI Analyzer API",
        "version": "1.0.0",
        "description": "AI-powered pharmacogenomic analysis based on CPIC guidelines",
        "endpoints": {
            "/analyze": "POST - Analyze VCF file for drug-gene interaction",
            "/supported-drugs": "GET - List supported drugs",
            "/supported-genes": "GET - List supported genes",
            "/drug-info": "GET - Get information about a specific drug",
            "/health": "GET - Health check"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "services": {
            "risk_engine": "operational",
            "llm_service": "available" if llm_service.client else "fallback mode"
        }
    }

@app.get("/supported-drugs")
async def get_drugs():
    """Get list of supported drugs."""
    return {
        "drugs": get_supported_drugs(),
        "count": len(get_supported_drugs())
    }

@app.get("/supported-genes")
async def get_genes():
    """Get list of supported genes."""
    return {
        "genes": get_supported_genes(),
        "count": len(get_supported_genes())
    }

@app.get("/drug-info/{drug}")
async def get_drug_info(drug: str):
    """Get information about a specific drug."""
    from cpic_guidelines import get_gene_for_drug, get_reference_drug_for_gene, CPIC_GUIDELINES
    
    gene = get_gene_for_drug(drug.upper())
    
    if not gene:
        raise HTTPException(status_code=404, detail=f"Drug '{drug}' not found")
    
    reference_drug = get_reference_drug_for_gene(gene, drug)

    if gene not in CPIC_GUIDELINES or not reference_drug:
        raise HTTPException(status_code=404, detail=f"No guidelines found for {drug}")
    
    guidelines = CPIC_GUIDELINES[gene][reference_drug]
    
    return {
        "drug": drug.upper(),
        "gene": gene,
        "guideline_source_drug": reference_drug,
        "diplotypes": list(guidelines["diplotypes"].keys()),
        "phenotypes": list(guidelines["phenotype_risk"].keys()),
        "common_variants": guidelines.get("common_variants", [])
    }

@app.post("/analyze")
async def analyze(
    vcf_file: UploadFile = File(...),
    drug: str = Form(...),
    patient_id: Optional[str] = Form("PATIENT_001"),
    use_llm: bool = Form(True)
):
    """
    Analyze VCF file for drug-gene interaction risk.
    
    Args:
        vcf_file: VCF file upload
        drug: Drug name to analyze
        patient_id: Optional patient ID
        use_llm: Whether to use LLM for enhanced explanations
        
    Returns:
        Complete risk assessment with clinical recommendations
    """
    try:
        # Read VCF content
        vcf_content = await vcf_file.read()
        vcf_text = _decode_vcf_upload(vcf_file, vcf_content)
        
        # Validate VCF content
        if not _looks_like_vcf(vcf_text):
            raise HTTPException(status_code=400, detail="Invalid VCF file format")
        
        # Run risk analysis
        result = risk_engine.analyze(vcf_text, drug, patient_id)
        
        # Enhance with LLM if requested and available
        if use_llm:
            result = llm_service.generate_explanation(result)
            
            # Generate Doctor Discussion Card (unique feature)
            doctor_card = llm_service.generate_doctor_discussion_card(result)
            result["smart_patient_guidance"] = {
                "doctor_discussion_card": doctor_card,
                "unique_feature": "AI-powered personalized medication guidance"
            }
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.post("/analyze/json")
async def analyze_json(request: AnalyzeRequest):
    """
    Analyze VCF content provided as JSON string.
    
    Args:
        request: AnalyzeRequest with vcf_content, drug, patient_id, use_llm
        
    Returns:
        Complete risk assessment with clinical recommendations
    """
    try:
        # Validate VCF content
        if not request.vcf_content.strip():
            raise HTTPException(status_code=400, detail="Empty VCF content")
        
        if not _looks_like_vcf(request.vcf_content):
            raise HTTPException(status_code=400, detail="Invalid VCF file format")
        
        # Run risk analysis
        result = risk_engine.analyze(request.vcf_content, request.drug, request.patient_id)
        
        # Enhance with LLM if requested and available
        if request.use_llm:
            result = llm_service.generate_explanation(result)
            
            # Generate Doctor Discussion Card (unique feature)
            doctor_card = llm_service.generate_doctor_discussion_card(result)
            result["smart_patient_guidance"] = {
                "doctor_discussion_card": doctor_card,
                "unique_feature": "AI-powered personalized medication guidance"
            }
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal server error: {str(exc)}"}
    )

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)
