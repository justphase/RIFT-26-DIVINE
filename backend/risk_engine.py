"""
Risk Engine Module for Pharmacogenomic Analysis
Maps diplotypes to phenotypes and risk labels based on CPIC guidelines.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from cpic_guidelines import (
    get_gene_for_drug,
    get_reference_drug_for_gene,
    get_phenotype_from_diplotype,
    get_risk_assessment,
    get_alternative_drugs,
    get_supported_drugs,
    get_supported_genes,
    CPIC_GUIDELINES,
    PHENOTYPE_TYPES
)
from vcf_parser import Variant, VCFParser

@dataclass
class RiskResult:
    """Result of pharmacogenomic risk assessment."""
    patient_id: str
    drug: str
    timestamp: str
    risk_label: str
    confidence_score: float
    severity: str
    primary_gene: str
    diplotype: str
    phenotype: str
    detected_variants: List[Dict]
    action: str
    alternative_suggestion: Optional[str]
    cpic_guideline_link: str

class RiskEngine:
    """Risk engine for pharmacogenomic analysis."""
    
    def __init__(self):
        self.parser = VCFParser()
        self.supported_drugs = get_supported_drugs()
        self.supported_genes = get_supported_genes()
    
    def analyze(self, vcf_content: str, drug: str, patient_id: str = "PATIENT_001") -> Dict:
        """
        Analyze VCF file for drug-gene interaction risk.
        
        Args:
            vcf_content: Content of the VCF file
            drug: Drug name to analyze
            patient_id: Patient identifier
            
        Returns:
            Dictionary with complete risk assessment
        """
        import datetime
        
        # Normalize drug name
        drug_upper = drug.upper()
        
        # Get gene for drug
        gene = get_gene_for_drug(drug_upper)
        
        if not gene:
            return self._create_error_result(
                patient_id, 
                drug, 
                f"Drug '{drug}' is not supported. Supported drugs: {', '.join(self.supported_drugs)}"
            )
        
        # Parse VCF file
        variants = self.parser.parse_vcf_content(vcf_content)
        sample_id = self.parser.metadata.get("sample_id", patient_id)
        
        # Get variants for the specific gene
        gene_variants = self.parser.get_variants_for_gene(gene, variants)
        
        # Infer diplotype from variants
        diplotype = self.parser.infer_diplotype(gene, gene_variants)
        
        # Get phenotype from diplotype
        phenotype = get_phenotype_from_diplotype(gene, drug_upper, diplotype)
        
        # Get risk assessment
        risk_info = get_risk_assessment(gene, drug_upper, phenotype)
        
        # Get alternative drugs
        alternatives = get_alternative_drugs(drug_upper)
        alternative_suggestion = alternatives[0] if alternatives and risk_info.get("risk_label") in ["Toxic", "Ineffective"] else None
        
        # Format detected variants
        detected_variants = []
        for v in gene_variants:
            detected_variants.append({
                "rsid": v.rsid,
                "genotype": v.genotype
            })
        
        # If no variants found for gene, provide default
        if not detected_variants:
            detected_variants = [{"rsid": "Not detected", "genotype": "N/A"}]
        
        # Calculate confidence score based on variant detection
        confidence_score = self._calculate_confidence(gene, gene_variants)
        
        # Create result
        result = {
            "patient_id": sample_id,
            "drug": drug_upper,
            "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
            "risk_assessment": {
                "risk_label": risk_info.get("risk_label", "Unknown"),
                "confidence_score": confidence_score,
                "severity": risk_info.get("severity", "unknown")
            },
            "pharmacogenomic_profile": {
                "primary_gene": gene,
                "diplotype": diplotype,
                "phenotype": phenotype,
                "detected_variants": detected_variants
            },
            "clinical_recommendation": {
                "action": risk_info.get("action", "Consult physician"),
                "alternative_suggestion": alternative_suggestion,
                "cpic_guideline_link": risk_info.get("cpic_url", "https://cpicpgx.org/")
            },
            "patient_advice": {
                "patient_friendly_summary": self._generate_patient_summary(gene, drug_upper, phenotype, risk_info.get("risk_label", "Unknown")),
                "best_medicine_suggestion": f"Consider {alternative_suggestion}" if alternative_suggestion else "Current medication is appropriate for your genetic profile",
                "doctor_talking_points": self._generate_doctor_talking_points(gene, drug_upper, phenotype, risk_info.get("risk_label", "Unknown"), alternative_suggestion)
            },
            "llm_generated_explanation": {
                "summary": f"The {gene} gene encodes {self._get_gene_description(gene)}. Your genotype {diplotype} results in a {phenotype} phenotype, which means you have {self._get_phenotype_description(phenotype)}. This {risk_info.get('risk_label', 'Unknown')} risk level for {drug_upper} is based on CPIC guidelines."
            },
            "quality_metrics": {
                "vcf_parsing_success": True,
                "gene_detected": gene in [v.gene for v in variants] or len(gene_variants) > 0,
                "variants_found": len(gene_variants)
            }
        }
        
        return result
    
    def _calculate_confidence(self, gene: str, variants: List[Variant]) -> float:
        """Calculate confidence score based on detected variants."""
        if not variants:
            return 0.3  # Low confidence if no variants found
        
        # Check for known functional variants
        known_variants = self.parser.RSID_TO_ALLELE.keys()
        detected_known = sum(1 for v in variants if v.rsid in known_variants)
        
        if detected_known > 0:
            return min(0.95, 0.5 + (detected_known * 0.15))
        
        return 0.6  # Moderate confidence for unknown variants
    
    def _get_gene_description(self, gene: str) -> str:
        """Get human-readable gene description."""
        descriptions = {
            "CYP2D6": "an enzyme responsible for metabolizing about 25% of commonly prescribed drugs",
            "CYP2C19": "an enzyme involved in activating or metabolizing many drugs including clopidogrel and proton pump inhibitors",
            "CYP2C9": "an enzyme that metabolizes warfarin and other drugs",
            "SLCO1B1": "a transporter protein that affects statin uptake and efficacy",
            "TPMT": "an enzyme that metabolizes thiopurine drugs used in immunosuppression",
            "DPYD": "an enzyme responsible for metabolizing fluorouracil and other fluoropyrimidines"
        }
        return descriptions.get(gene, "a drug-metabolizing enzyme")
    
    def _get_phenotype_description(self, phenotype: str) -> str:
        """Get human-readable phenotype description."""
        descriptions = {
            "PM": "reduced or absent enzyme activity",
            "IM": "reduced enzyme activity",
            "NM": "normal enzyme activity",
            "RM": "increased enzyme activity",
            "URM": "greatly increased enzyme activity"
        }
        return descriptions.get(phenotype, "unknown enzyme activity")
    
    def _generate_patient_summary(self, gene: str, drug: str, phenotype: str, risk_label: str) -> str:
        """Generate patient-friendly summary."""
        phenotype_full = PHENOTYPE_TYPES.get(phenotype, "Unknown")
        
        summaries = {
            "Safe": f"Good news! Based on your {gene} gene analysis, your body processes {drug} normally. You can take this medication as prescribed by your doctor.",
            "Adjust Dosage": f"Based on your {gene} gene analysis, your body processes {drug} differently than average. Your doctor may need to adjust your dose for best results.",
            "Toxic": f"Warning: Your {gene} gene analysis shows you may be at risk for serious side effects from {drug}. It's important to discuss alternative medications with your doctor.",
            "Ineffective": f"Based on your {gene} gene analysis, {drug} may not work well for you. Your doctor may want to consider a different medication."
        }
        
        return summaries.get(risk_label, f"Your {gene} gene analysis shows a {phenotype_full} phenotype for {drug}. Please consult your healthcare provider.")
    
    def _generate_doctor_talking_points(self, gene: str, drug: str, phenotype: str, risk_label: str, alternative: Optional[str]) -> List[str]:
        """Generate doctor discussion points."""
        phenotype_full = PHENOTYPE_TYPES.get(phenotype, "Unknown")
        
        base_points = [
            f"Pharmacogenomic testing shows {phenotype_full} for {gene} gene",
            f"CPIC guidelines recommend considering this result when prescribing {drug}"
        ]
        
        if risk_label == "Toxic":
            base_points.extend([
                f"Consider alternative: {alternative}" if alternative else "Consider alternative medication",
                "Recommended: Avoid standard dosing due to toxicity risk",
                "Consider genetic-guided dose reduction or alternative therapy"
            ])
        elif risk_label == "Ineffective":
            base_points.extend([
                f"Consider alternative: {alternative}" if alternative else "Consider alternative medication",
                "Patient may not achieve therapeutic response at standard doses",
                "Consider therapeutic drug monitoring"
            ])
        elif risk_label == "Adjust Dosage":
            base_points.extend([
                "Dose adjustment may be needed based on genotype",
                "Consider starting at lower end of dose range",
                "Therapeutic drug monitoring recommended"
            ])
        else:
            base_points.extend([
                "Standard dosing appropriate",
                "No specific genotype-guided adjustments needed"
            ])
        
        return base_points[:3]  # Return max 3 points
    
    def _create_error_result(self, patient_id: str, drug: str, error_message: str) -> Dict:
        """Create error result."""
        import datetime
        return {
            "patient_id": patient_id,
            "drug": drug.upper(),
            "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
            "risk_assessment": {
                "risk_label": "Error",
                "confidence_score": 0.0,
                "severity": "unknown"
            },
            "pharmacogenomic_profile": {
                "primary_gene": "Unknown",
                "diplotype": "Unknown",
                "phenotype": "Unknown",
                "detected_variants": []
            },
            "clinical_recommendation": {
                "action": error_message,
                "alternative_suggestion": None,
                "cpic_guideline_link": "https://cpicpgx.org/"
            },
            "patient_advice": {
                "patient_friendly_summary": "An error occurred during analysis. Please try again with a valid VCF file.",
                "best_medicine_suggestion": "Consult your healthcare provider",
                "doctor_talking_points": ["Error in analysis - please retry"]
            },
            "llm_generated_explanation": {
                "summary": error_message
            },
            "quality_metrics": {
                "vcf_parsing_success": False
            }
        }
    
    def get_supported_drugs_info(self) -> Dict:
        """Get information about supported drugs."""
        info = {}
        for drug in self.supported_drugs:
            gene = get_gene_for_drug(drug)
            reference_drug = get_reference_drug_for_gene(gene, drug) if gene else None
            phenotypes = []
            if gene in CPIC_GUIDELINES and reference_drug in CPIC_GUIDELINES[gene]:
                phenotypes = list(CPIC_GUIDELINES[gene][reference_drug]["phenotype_risk"].keys())
            info[drug] = {
                "gene": gene,
                "guideline_source_drug": reference_drug,
                "phenotypes": phenotypes,
            }
        return info
