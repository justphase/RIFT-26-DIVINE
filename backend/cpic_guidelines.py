"""
CPIC Guidelines for Pharmacogenomic Testing
Implements dosing guidelines for 6 critical genes:
- CYP2D6, CYP2C19, CYP2C9, SLCO1B1, TPMT, DPYD
"""

# Gene to Drug Mapping
GENE_DRUG_MAPPING = {
    "CYP2D6": ["CODEINE", "TRAMADOL", "METOPROLOL"],
    "CYP2C19": ["CLOPIDOGREL", "OMEPRAZOLE", "LANSOPRAZOLE"],
    "CYP2C9": ["WARFARIN", "LOSARTAN", "PHENYTOIN"],
    "SLCO1B1": ["SIMVASTATIN", "ATORVASTATIN", "ROSUVASTATIN"],
    "TPMT": ["AZATHIOPRINE", "MERCAPTOPURINE", "THIOGUANINE"],
    "DPYD": ["FLUOROURACIL", "CAPECITABINE", "TEGAFUR"]
}

# Drug to Gene Mapping (reverse)
DRUG_GENE_MAPPING = {}
for gene, drugs in GENE_DRUG_MAPPING.items():
    for drug in drugs:
        DRUG_GENE_MAPPING[drug] = gene

# Phenotype Definitions
PHENOTYPE_TYPES = {
    "PM": "Poor Metabolizer",
    "IM": "Intermediate Metabolizer", 
    "NM": "Normal Metabolizer",
    "RM": "Rapid Metabolizer",
    "URM": "Ultrarapid Metabolizer",
    "Unknown": "Unknown"
}

# CPIC Guidelines: Gene -> Diplotype -> Phenotype -> Risk -> Recommendation
# Based on CPIC guidelines (https://cpicpgx.org/)

CPIC_GUIDELINES = {
    "CYP2D6": {
        "CODEINE": {
            "diplotypes": {
                "*1/*1": "NM",
                "*1/*2": "RM", 
                "*1/*3": "IM",
                "*1/*4": "PM",
                "*2/*2": "RM",
                "*2/*3": "IM",
                "*2/*4": "PM",
                "*3/*3": "PM",
                "*3/*4": "PM",
                "*4/*4": "PM",
                "*1xN/*1": "URM",
                "*1xN/*2": "URM",
                "*2xN/*2": "URM"
            },
            "phenotype_risk": {
                "PM": {
                    "risk_label": "Toxic",
                    "severity": "critical",
                    "action": "Avoid Codeine - Risk of life-threatening toxicity",
                    "alternative": "Morphine or Non-Opioid Analgesic",
                    "cpic_url": "https://cpicpgx.org/guidelines/cyp2d6-codeine-guideline/"
                },
                "IM": {
                    "risk_label": "Adjust Dosage", 
                    "severity": "moderate",
                    "action": "Use lowest effective dose, consider alternative",
                    "alternative": "Tramadol with monitoring or Non-Opioid",
                    "cpic_url": "https://cpicpgx.org/guidelines/cyp2d6-codeine-guideline/"
                },
                "NM": {
                    "risk_label": "Safe",
                    "severity": "none",
                    "action": "Use label-recommended dosing",
                    "alternative": None,
                    "cpic_url": "https://cpicpgx.org/guidelines/cyp2d6-codeine-guideline/"
                },
                "RM": {
                    "risk_label": "Safe",
                    "severity": "none",
                    "action": "Use label-recommended dosing",
                    "alternative": None,
                    "cpic_url": "https://cpicpgx.org/guidelines/cyp2d6-codeine-guideline/"
                },
                "URM": {
                    "risk_label": "Ineffective",
                    "severity": "critical",
                    "action": "Avoid Codeine - Risk of inadequate analgesia",
                    "alternative": "Morphine or Non-Opioid Analgesic",
                    "cpic_url": "https://cpicpgx.org/guidelines/cyp2d6-codeine-guideline/"
                }
            },
            "common_variants": ["rs3892097", "rs1065852", "rs5030655", "rs5030867", "rs28371725", "rs28413332", "rs28413331"]
        }
    },
    "CYP2C19": {
        "CLOPIDOGREL": {
            "diplotypes": {
                "*1/*1": "NM",
                "*1/*2": "PM",
                "*1/*3": "IM",
                "*2/*2": "PM",
                "*2/*3": "PM",
                "*3/*3": "PM",
                "*17/*17": "RM",
                "*1/*17": "RM"
            },
            "phenotype_risk": {
                "PM": {
                    "risk_label": "Ineffective",
                    "severity": "high",
                    "action": "Avoid Clopidogrel - Poor activation",
                    "alternative": "Prasugrel or Ticagrelor (if no contraindication)",
                    "cpic_url": "https://cpicpgx.org/guidelines/cyp2c19-clopidogrel-guideline/"
                },
                "IM": {
                    "risk_label": "Adjust Dosage",
                    "severity": "moderate", 
                    "action": "Consider alternative antiplatelet therapy",
                    "alternative": "Prasugrel or Ticagrelor",
                    "cpic_url": "https://cpicpgx.org/guidelines/cyp2c19-clopidogrel-guideline/"
                },
                "NM": {
                    "risk_label": "Safe",
                    "severity": "none",
                    "action": "Use label-recommended dosing",
                    "alternative": None,
                    "cpic_url": "https://cpicpgx.org/guidelines/cyp2c19-clopidogrel-guideline/"
                },
                "RM": {
                    "risk_label": "Safe",
                    "severity": "none", 
                    "action": "Use label-recommended dosing",
                    "alternative": None,
                    "cpic_url": "https://cpicpgx.org/guidelines/cyp2c19-clopidogrel-guideline/"
                },
                "URM": {
                    "risk_label": "Safe",
                    "severity": "none",
                    "action": "Use label-recommended dosing",
                    "alternative": None,
                    "cpic_url": "https://cpicpgx.org/guidelines/cyp2c19-clopidogrel-guideline/"
                }
            },
            "common_variants": ["rs4244285", "rs4986893", "rs12248560", "rs28399504", "rs41291556"]
        }
    },
    "CYP2C9": {
        "WARFARIN": {
            "diplotypes": {
                "*1/*1": "NM",
                "*1/*2": "IM",
                "*1/*3": "IM",
                "*2/*2": "PM",
                "*2/*3": "PM",
                "*3/*3": "PM"
            },
            "phenotype_risk": {
                "PM": {
                    "risk_label": "Toxic",
                    "severity": "critical",
                    "action": "Reduce warfarin dose by 50-70%, frequent INR monitoring",
                    "alternative": "Consider alternative anticoagulant (e.g., apixaban, rivaroxaban)",
                    "cpic_url": "https://cpicpgx.org/guidelines/cyp2c9-warfarin-guideline/"
                },
                "IM": {
                    "risk_label": "Adjust Dosage",
                    "severity": "moderate",
                    "action": "Reduce initial dose, frequent INR monitoring",
                    "alternative": None,
                    "cpic_url": "https://cpicpgx.org/guidelines/cyp2c9-warfarin-guideline/"
                },
                "NM": {
                    "risk_label": "Safe",
                    "severity": "none",
                    "action": "Use standard dosing with routine INR monitoring",
                    "alternative": None,
                    "cpic_url": "https://cpicpgx.org/guidelines/cyp2c9-warfarin-guideline/"
                },
                "RM": {
                    "risk_label": "Safe",
                    "severity": "none",
                    "action": "Use standard dosing with routine INR monitoring",
                    "alternative": None,
                    "cpic_url": "https://cpicpgx.org/guidelines/cyp2c9-warfarin-guideline/"
                },
                "URM": {
                    "risk_label": "Safe",
                    "severity": "none",
                    "action": "Use standard dosing with routine INR monitoring",
                    "alternative": None,
                    "cpic_url": "https://cpicpgx.org/guidelines/cyp2c9-warfarin-guideline/"
                }
            },
            "common_variants": ["rs1799853", "rs1057910", "rs28371686", "rs4917639", "rs7900194"]
        }
    },
    "SLCO1B1": {
        "SIMVASTATIN": {
            "diplotypes": {
                "*1/*1": "NM",
                "*1/*5": "IM",
                "*5/*5": "PM",
                "*1/*15": "IM",
                "*15/*15": "PM"
            },
            "phenotype_risk": {
                "PM": {
                    "risk_label": "Toxic",
                    "severity": "high",
                    "action": "Avoid simvastatin >20mg daily, use alternate statin",
                    "alternative": "Atorvastatin, Rosuvastatin, or Pravastatin",
                    "cpic_url": "https://cpicpgx.org/guidelines/slco1b1-simvastatin-guideline/"
                },
                "IM": {
                    "risk_label": "Adjust Dosage",
                    "severity": "moderate",
                    "action": "Use simvastatin 20mg max, consider alternate statin",
                    "alternative": "Atorvastatin, Rosuvastatin, or Pravastatin",
                    "cpic_url": "https://cpicpgx.org/guidelines/slco1b1-simvastatin-guideline/"
                },
                "NM": {
                    "risk_label": "Safe",
                    "severity": "none",
                    "action": "Use standard dosing",
                    "alternative": None,
                    "cpic_url": "https://cpicpgx.org/guidelines/slco1b1-simvastatin-guideline/"
                },
                "RM": {
                    "risk_label": "Safe",
                    "severity": "none",
                    "action": "Use standard dosing",
                    "alternative": None,
                    "cpic_url": "https://cpicpgx.org/guidelines/slco1b1-simvastatin-guideline/"
                },
                "URM": {
                    "risk_label": "Safe",
                    "severity": "none",
                    "action": "Use standard dosing",
                    "alternative": None,
                    "cpic_url": "https://cpicpgx.org/guidelines/slco1b1-simvastatin-guideline/"
                }
            },
            "common_variants": ["rs4149056", "rs4149015", "rs2304130", "rs4363657", "rs4149268"]
        }
    },
    "TPMT": {
        "AZATHIOPRINE": {
            "diplotypes": {
                "*1/*1": "NM",
                "*1/*3A": "IM",
                "*1/*3B": "IM", 
                "*1/*3C": "IM",
                "*3A/*3A": "PM",
                "*3A/*3B": "PM",
                "*3B/*3B": "PM",
                "*3A/*3C": "PM",
                "*3C/*3C": "PM"
            },
            "phenotype_risk": {
                "PM": {
                    "risk_label": "Toxic",
                    "severity": "critical",
                    "action": "Avoid azathioprine - severe myelosuppression risk",
                    "alternative": "Consider mycophenolate mofetil or tacrolimus",
                    "cpic_url": "https://cpicpgx.org/guidelines/tpmt-azathioprine-guideline/"
                },
                "IM": {
                    "risk_label": "Adjust Dosage",
                    "severity": "high",
                    "action": "Reduce dose to 30-50% of normal, monitor closely",
                    "alternative": None,
                    "cpic_url": "https://cpicpgx.org/guidelines/tpmt-azathioprine-guideline/"
                },
                "NM": {
                    "risk_label": "Safe",
                    "severity": "none",
                    "action": "Use standard dosing",
                    "alternative": None,
                    "cpic_url": "https://cpicpgx.org/guidelines/tpmt-azathioprine-guideline/"
                },
                "RM": {
                    "risk_label": "Safe",
                    "severity": "none",
                    "action": "Use standard dosing",
                    "alternative": None,
                    "cpic_url": "https://cpicpgx.org/guidelines/tpmt-azathioprine-guideline/"
                },
                "URM": {
                    "risk_label": "Safe",
                    "severity": "none",
                    "action": "Use standard dosing",
                    "alternative": None,
                    "cpic_url": "https://cpicpgx.org/guidelines/tpmt-azathioprine-guideline/"
                }
            },
            "common_variants": ["rs1800462", "rs1800588", "rs1142345", "rs1800589", "rs12239046"]
        }
    },
    "DPYD": {
        "FLUOROURACIL": {
            "diplotypes": {
                "*1/*1": "NM",
                "*1/*2": "IM",
                "*1/*13": "IM",
                "*1/*14": "IM",
                "*2/*2": "PM",
                "*13/*13": "PM",
                "*1A/*1": "NM",
                "*1A/*2": "IM"
            },
            "phenotype_risk": {
                "PM": {
                    "risk_label": "Toxic",
                    "severity": "critical",
                    "action": "Avoid fluorouracil - severe toxicity risk",
                    "alternative": "Non-FU containing regimen, consult oncology",
                    "cpic_url": "https://cpicpgx.org/guidelines/dpd-fluorouracil-guideline/"
                },
                "IM": {
                    "risk_label": "Adjust Dosage",
                    "severity": "high",
                    "action": "Reduce initial dose by 50%, monitor closely",
                    "alternative": None,
                    "cpic_url": "https://cpicpgx.org/guidelines/dpd-fluorouracil-guideline/"
                },
                "NM": {
                    "risk_label": "Safe",
                    "severity": "none",
                    "action": "Use standard dosing",
                    "alternative": None,
                    "cpic_url": "https://cpicpgx.org/guidelines/dpd-fluorouracil-guideline/"
                },
                "RM": {
                    "risk_label": "Safe",
                    "severity": "none",
                    "action": "Use standard dosing",
                    "alternative": None,
                    "cpic_url": "https://cpicpgx.org/guidelines/dpd-fluorouracil-guideline/"
                },
                "URM": {
                    "risk_label": "Safe",
                    "severity": "none",
                    "action": "Use standard dosing",
                    "alternative": None,
                    "cpic_url": "https://cpicpgx.org/guidelines/dpd-fluorouracil-guideline/"
                }
            },
            "common_variants": ["rs3918290", "rs55886062", "rs67376798", "rs55886062", "rs75017182", "rs67376798", "rs56038477"]
        }
    }
}

# Alternative drugs mapping for each primary drug
ALTERNATIVE_DRUGS = {
    "CODEINE": ["Morphine", "Hydromorphone", "Non-Opioid Analgesic (Ibuprofen/Acetaminophen)"],
    "TRAMADOL": ["Oxycodone", "Non-Opioid Analgesic"],
    "METOPROLOL": ["Atenolol", "Bisoprolol", "Carvedilol"],
    "CLOPIDOGREL": ["Prasugrel", "Ticagrelor", "Aspirin"],
    "OMEPRAZOLE": ["Pantoprazole", "Rabeprazole", "Famotidine"],
    "LANSOPRAZOLE": ["Pantoprazole", "Rabeprazole", "Famotidine"],
    "WARFARIN": ["Apixaban", "Rivaroxaban", "Dabigatran"],
    "LOSARTAN": ["Valsartan", "Irbesartan", "Candesartan"],
    "PHENYTOIN": ["Levetiracetam", "Lamotrigine", "Carbamazepine"],
    "SIMVASTATIN": ["Atorvastatin", "Rosuvastatin", "Pravastatin"],
    "ATORVASTATIN": ["Rosuvastatin", "Pravastatin", "Fluvastatin"],
    "ROSUVASTATIN": ["Atorvastatin", "Pravastatin", "Fluvastatin"],
    "AZATHIOPRINE": ["Mycophenolate Mofetil", "Tacrolimus", "Methotrexate"],
    "MERCAPTOPURINE": ["Mycophenolate Mofetil", "Azathioprine"],
    "THIOGUANINE": ["Mycophenolate Mofetil", "Azathioprine"],
    "FLUOROURACIL": ["Non-FU containing regimen", "Consult Oncology", "Capecitabine (with dose adjustment)"],
    "CAPECITABINE": ["Non-FU containing regimen", "Consult Oncology"],
    "TEGAFUR": ["Non-FU containing regimen", "Consult Oncology"]
}

def get_gene_for_drug(drug: str) -> str:
    """Get the primary gene associated with a drug."""
    return DRUG_GENE_MAPPING.get(drug.upper(), None)

def get_reference_drug_for_gene(gene: str, drug: str) -> str:
    """Resolve to a guideline-backed drug for a gene when a direct entry is unavailable."""
    drug_upper = drug.upper()
    gene_guidelines = CPIC_GUIDELINES.get(gene, {})
    if drug_upper in gene_guidelines:
        return drug_upper

    if gene_guidelines:
        return next(iter(gene_guidelines.keys()))
    return None

def get_phenotype_from_diplotype(gene: str, drug: str, diplotype: str) -> str:
    """Map diplotype to phenotype."""
    reference_drug = get_reference_drug_for_gene(gene, drug)
    if gene in CPIC_GUIDELINES and reference_drug in CPIC_GUIDELINES[gene]:
        diplotype_map = CPIC_GUIDELINES[gene][reference_drug].get("diplotypes", {})
        return diplotype_map.get(diplotype, "Unknown")
    return "Unknown"

def get_risk_assessment(gene: str, drug: str, phenotype: str) -> dict:
    """Get risk assessment based on phenotype."""
    reference_drug = get_reference_drug_for_gene(gene, drug)
    if gene in CPIC_GUIDELINES and reference_drug in CPIC_GUIDELINES[gene]:
        phenotype_risk = CPIC_GUIDELINES[gene][reference_drug].get("phenotype_risk", {})
        return phenotype_risk.get(phenotype, {
            "risk_label": "Unknown",
            "severity": "unknown",
            "action": "Consult physician",
            "alternative": None,
            "cpic_url": "https://cpicpgx.org/"
        })
    return {
        "risk_label": "Unknown",
        "severity": "unknown", 
        "action": "Consult physician",
        "alternative": None,
        "cpic_url": "https://cpicpgx.org/"
    }

def get_alternative_drugs(drug: str) -> list:
    """Get list of alternative drugs."""
    return ALTERNATIVE_DRUGS.get(drug.upper(), ["Consult your physician"])

def get_supported_drugs() -> list:
    """Get list of all supported drugs."""
    return list(DRUG_GENE_MAPPING.keys())

def get_supported_genes() -> list:
    """Get list of all supported genes."""
    return list(GENE_DRUG_MAPPING.keys())
