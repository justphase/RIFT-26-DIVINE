"""
LLM service for clinical explanations.
Uses OpenAI when available, and falls back to deterministic templates.
"""

import os
from typing import Dict, Optional

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except Exception:
    OPENAI_AVAILABLE = False


class LLMService:
    """Service for generating AI-powered clinical explanations."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.client = None
        if OPENAI_AVAILABLE and self.api_key:
            try:
                self.client = OpenAI(api_key=self.api_key)
            except Exception:
                self.client = None

    def _chat_complete(self, prompt: str, system_prompt: str, model: str, max_tokens: int, temperature: float) -> Optional[str]:
        if not self.client:
            return None
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=max_tokens,
                temperature=temperature,
            )
            message = response.choices[0].message.content
            return message.strip() if message else None
        except Exception:
            return None

    def generate_explanation(self, analysis_result: Dict, model: str = "gpt-4o-mini") -> Dict:
        """Generate explanation and patient advice with safe fallback."""
        if not self.client:
            return self._generate_fallback_explanation(analysis_result)

        prompt = self._build_explanation_prompt(analysis_result)
        llm_summary = self._chat_complete(
            prompt=prompt,
            system_prompt=(
                "You are a clinical pharmacogenomics expert. "
                "Provide concise, accurate, patient-safe explanations aligned with CPIC."
            ),
            model=model,
            max_tokens=500,
            temperature=0.2,
        )
        if not llm_summary:
            return self._generate_fallback_explanation(analysis_result)

        result = analysis_result.copy()
        result["llm_generated_explanation"] = {
            "summary": llm_summary,
            "model_used": model,
            "generated": True,
        }

        patient_prompt = self._build_patient_advice_prompt(analysis_result)
        patient_advice = self._chat_complete(
            prompt=patient_prompt,
            system_prompt=(
                "You are a patient education specialist. "
                "Write plain-language medication guidance with practical next steps."
            ),
            model=model,
            max_tokens=350,
            temperature=0.4,
        )
        if patient_advice:
            result["patient_advice"]["patient_friendly_summary"] = patient_advice
            result["patient_advice"]["llm_enhanced"] = True

        return result

    def _build_explanation_prompt(self, result: Dict) -> str:
        profile = result.get("pharmacogenomic_profile", {})
        risk = result.get("risk_assessment", {})
        clinical = result.get("clinical_recommendation", {})
        return f"""
Provide a clinical explanation for this pharmacogenomic analysis.

Gene: {profile.get('primary_gene', 'Unknown')}
Diplotype: {profile.get('diplotype', 'Unknown')}
Phenotype: {profile.get('phenotype', 'Unknown')}
Drug: {result.get('drug', 'Unknown')}
Risk: {risk.get('risk_label', 'Unknown')}
Severity: {risk.get('severity', 'Unknown')}
Recommendation: {clinical.get('action', 'N/A')}
Alternative: {clinical.get('alternative_suggestion', 'None')}

Include:
1) Mechanism
2) Why genotype maps to this risk
3) CPIC-aligned implication
4) Practical clinical note
""".strip()

    def _build_patient_advice_prompt(self, result: Dict) -> str:
        profile = result.get("pharmacogenomic_profile", {})
        risk = result.get("risk_assessment", {})
        return f"""
Write patient-friendly advice in plain language.

Gene result: {profile.get('primary_gene', 'Unknown')} - {profile.get('phenotype', 'Unknown')}
Drug: {result.get('drug', 'Unknown')}
Risk: {risk.get('risk_label', 'Unknown')}

Provide:
1) Short summary
2) What this means for treatment
3) One action for the patient
4) 2-3 things to discuss with their doctor
""".strip()

    def _generate_fallback_explanation(self, result: Dict) -> Dict:
        profile = result.get("pharmacogenomic_profile", {})
        risk = result.get("risk_assessment", {})
        gene = profile.get("primary_gene", "Unknown")
        diplotype = profile.get("diplotype", "Unknown")
        phenotype = profile.get("phenotype", "Unknown")
        drug = result.get("drug", "Unknown")
        label = risk.get("risk_label", "Unknown")

        explanation = self._generate_template_explanation(gene, diplotype, phenotype, drug, label)
        result["llm_generated_explanation"] = {
            "summary": explanation,
            "model_used": "template",
            "generated": False,
        }
        return result

    def _generate_template_explanation(self, gene: str, diplotype: str, phenotype: str, drug: str, risk_label: str) -> str:
        gene_mechanisms = {
            "CYP2D6": "CYP2D6 is a key enzyme for many drugs, including several analgesics and cardiovascular agents.",
            "CYP2C19": "CYP2C19 affects activation and metabolism of antiplatelets and acid suppression therapies.",
            "CYP2C9": "CYP2C9 contributes to metabolism of anticoagulants and antiseizure medicines.",
            "SLCO1B1": "SLCO1B1 influences hepatic transport of statins and related myopathy risk.",
            "TPMT": "TPMT controls metabolism of thiopurines and toxicity risk from dose accumulation.",
            "DPYD": "DPYD is critical for fluoropyrimidine clearance; low activity can increase severe toxicity.",
        }
        phenotype_implications = {
            "PM": "very low/absent activity",
            "IM": "reduced activity",
            "NM": "expected activity",
            "RM": "increased activity",
            "URM": "markedly increased activity",
        }
        clinical_guidance = {
            "Safe": "Standard dosing is generally appropriate.",
            "Adjust Dosage": "Dose adjustment and closer monitoring are recommended.",
            "Toxic": "Avoid standard dosing due to elevated adverse effect risk.",
            "Ineffective": "Consider alternatives because therapeutic effect may be reduced.",
        }

        mechanism = gene_mechanisms.get(gene, "This gene affects drug handling in the body.")
        implication = phenotype_implications.get(phenotype, "uncertain activity")
        guidance = clinical_guidance.get(risk_label, "Clinical review is advised.")
        return (
            f"{mechanism} The diplotype {diplotype} maps to {phenotype} phenotype "
            f"({implication}), which supports a {risk_label} assessment for {drug}. {guidance}"
        )

    def generate_doctor_discussion_card(self, result: Dict) -> Dict:
        """Generate a concise doctor discussion card with LLM or template fallback."""
        prompt = f"""
Create a concise doctor discussion card.

Gene: {result.get('pharmacogenomic_profile', {}).get('primary_gene', 'Unknown')}
Phenotype: {result.get('pharmacogenomic_profile', {}).get('phenotype', 'Unknown')}
Drug: {result.get('drug', 'Unknown')}
Risk: {result.get('risk_assessment', {}).get('risk_label', 'Unknown')}
Alternative: {result.get('clinical_recommendation', {}).get('alternative_suggestion', 'None')}
""".strip()
        card_content = self._chat_complete(
            prompt=prompt,
            system_prompt="Create practical and brief talking points for a patient-doctor discussion.",
            model="gpt-4o-mini",
            max_tokens=260,
            temperature=0.4,
        )
        if card_content:
            return {
                "card_title": f"Pharmacogenomic Discussion: {result.get('drug', 'Drug')}",
                "card_content": card_content,
                "llm_generated": True,
            }
        return self._generate_template_doctor_card(result)

    def _generate_template_doctor_card(self, result: Dict) -> Dict:
        gene = result.get("pharmacogenomic_profile", {}).get("primary_gene", "Unknown")
        phenotype = result.get("pharmacogenomic_profile", {}).get("phenotype", "Unknown")
        drug = result.get("drug", "Unknown")
        risk = result.get("risk_assessment", {}).get("risk_label", "Unknown")
        alternative = result.get("clinical_recommendation", {}).get("alternative_suggestion", "an alternative")
        points = [
            f"My PGx result indicates {phenotype} status for {gene}.",
            f"My report labels {drug} as {risk} risk for me.",
            f"Should we consider {alternative} and a genotype-informed plan?",
            "What monitoring strategy do you recommend if this drug is continued?",
        ]
        return {
            "card_title": f"Discussion Point: {drug} and {gene}",
            "card_content": "\n".join([f"- {p}" for p in points]),
            "llm_generated": False,
        }
