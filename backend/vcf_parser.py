"""
VCF parser for extracting pharmacogenomic variants from VCF text.
Uses cyvcf2 when available, with a robust plain-text fallback parser.
"""

import os
import tempfile
from dataclasses import dataclass
from typing import Dict, List, Optional

try:
    import cyvcf2
    CYVCF2_AVAILABLE = True
except ImportError:
    CYVCF2_AVAILABLE = False


@dataclass
class Variant:
    """Represents a genetic variant from a VCF record."""

    chrom: str
    pos: int
    rsid: str
    ref: str
    alt: str
    genotype: str
    gene: Optional[str] = None


class VCFParser:
    """Parser for VCF v4.2 files."""

    GENE_CHROMOSOME_MAP = {
        "CYP2D6": "22",
        "CYP2C19": "10",
        "CYP2C9": "10",
        "SLCO1B1": "12",
        "TPMT": "6",
        "DPYD": "1",
    }

    GENE_RSID_MAP = {
        "CYP2D6": {
            "rs3892097": "*4 (splice defect)",
            "rs1065852": "*10",
            "rs5030655": "*6",
            "rs5030867": "*14",
            "rs28371725": "*2",
            "rs28413332": "*17",
            "rs28413331": "*29",
        },
        "CYP2C19": {
            "rs4244285": "*2 (loss of function)",
            "rs4986893": "*3 (loss of function)",
            "rs12248560": "*17 (gain of function)",
            "rs28399504": "*4",
            "rs41291556": "*5",
        },
        "CYP2C9": {
            "rs1799853": "*2 (reduced function)",
            "rs1057910": "*3 (no function)",
            "rs28371686": "*5",
            "rs4917639": "*11",
            "rs7900194": "*8",
        },
        "SLCO1B1": {
            "rs4149056": "*5 (reduced function)",
            "rs4149015": "*15",
            "rs2304130": "*14",
            "rs4363657": "*1a",
            "rs4149268": "*1b",
        },
        "TPMT": {
            "rs1800462": "*3A (no function)",
            "rs1800588": "*3B",
            "rs1142345": "*3B",
            "rs1800589": "*2",
            "rs12239046": "*4",
        },
        "DPYD": {
            "rs3918290": "*2A (no function)",
            "rs55886062": "*13",
            "rs67376798": "*14",
            "rs75017182": "*1",
            "rs56038477": "*5",
        },
    }

    RSID_TO_ALLELE = {
        "rs3892097": ("*4", "non-functional"),
        "rs1065852": ("*10", "reduced"),
        "rs5030655": ("*6", "non-functional"),
        "rs5030867": ("*14", "non-functional"),
        "rs28371725": ("*2", "normal"),
        "rs4244285": ("*2", "non-functional"),
        "rs4986893": ("*3", "non-functional"),
        "rs12248560": ("*17", "gain-of-function"),
        "rs1799853": ("*2", "reduced"),
        "rs1057910": ("*3", "non-functional"),
        "rs4149056": ("*5", "reduced"),
        "rs1800462": ("*3A", "non-functional"),
        "rs1800588": ("*3B", "non-functional"),
        "rs1142345": ("*3B", "non-functional"),
        "rs3918290": ("*2A", "non-functional"),
        "rs55886062": ("*13", "non-functional"),
        "rs67376798": ("*14", "reduced"),
    }

    def __init__(self):
        self.variants: List[Variant] = []
        self.metadata: Dict = {}

    def parse_vcf_content(self, vcf_content: str) -> List[Variant]:
        """Parse VCF text using cyvcf2 when possible, fallback otherwise."""
        if CYVCF2_AVAILABLE:
            try:
                return self._parse_with_cyvcf2(vcf_content)
            except Exception:
                pass
        return self._parse_fallback(vcf_content)

    def _parse_with_cyvcf2(self, vcf_content: str) -> List[Variant]:
        """Parse VCF content via cyvcf2 using a temporary file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".vcf", delete=False, encoding="utf-8") as temp_vcf:
            temp_vcf.write(vcf_content)
            temp_path = temp_vcf.name

        try:
            reader = cyvcf2.VCF(temp_path)
            self.metadata = {
                "sample_id": reader.samples[0] if reader.samples else "Unknown",
                "file_format": "VCF v4.2 (cyvcf2 parser)",
            }
            variants: List[Variant] = []
            for record in reader:
                rsid = record.ID if record.ID else "."
                gt = record.genotypes[0] if record.genotypes else [0, 0]
                genotype = self._format_genotype(gt, record.REF, record.ALT)
                variants.append(
                    Variant(
                        chrom=str(record.CHROM),
                        pos=int(record.POS),
                        rsid=rsid,
                        ref=str(record.REF),
                        alt=str(record.ALT[0]) if record.ALT else "",
                        genotype=genotype,
                    )
                )
            return variants
        finally:
            try:
                os.remove(temp_path)
            except OSError:
                pass

    def _parse_fallback(self, vcf_content: str) -> List[Variant]:
        """Plain-text parser for .vcf content."""
        variants: List[Variant] = []
        lines = vcf_content.strip().splitlines()
        sample_id = "Unknown"

        for line in lines:
            if line.startswith("#"):
                if line.startswith("#CHROM"):
                    parts = line.split("\t")
                    if len(parts) < 10:
                        parts = line.split()
                    if len(parts) >= 10:
                        sample_id = parts[9]
                continue

            if not line.strip():
                continue

            parts = line.split("\t")
            if len(parts) < 8:
                parts = line.split()
            if len(parts) < 8:
                continue

            try:
                pos = int(parts[1])
            except (TypeError, ValueError):
                continue

            chrom = parts[0]
            rsid = parts[2] if len(parts) > 2 else "."
            ref = parts[3]
            alt = parts[4].split(",")[0] if parts[4] else ""

            genotype = "Unknown"
            if len(parts) >= 10:
                format_fields = parts[8].split(":")
                sample_data = parts[9].split(":")
                gt_idx = format_fields.index("GT") if "GT" in format_fields else 0
                gt_value = sample_data[gt_idx] if gt_idx < len(sample_data) else "0/0"
                genotype = self._parse_genotype_string(gt_value, ref, alt)

            variants.append(
                Variant(
                    chrom=chrom,
                    pos=pos,
                    rsid=rsid,
                    ref=ref,
                    alt=alt,
                    genotype=genotype,
                )
            )

        self.metadata = {
            "sample_id": sample_id,
            "file_format": "VCF v4.2 (fallback parser)",
        }
        return variants

    def _format_genotype(self, gt: List[int], ref: str, alt: List[str]) -> str:
        """Format genotype list from cyvcf2 as alleles."""
        if not gt:
            return "Unknown"

        alleles = [ref] + list(alt)
        if len(gt) >= 2:
            a1 = alleles[gt[0]] if gt[0] < len(alleles) else "?"
            a2 = alleles[gt[1]] if gt[1] < len(alleles) else "?"
            return f"{a1}/{a2}"
        return "Unknown"

    def _parse_genotype_string(self, gt_string: str, ref: str, alt: str) -> str:
        """Parse genotype strings like 0/1, 1|1, 0/0."""
        if not gt_string or gt_string == ".":
            return f"{ref}/{ref}"

        parts = gt_string.replace("|", "/").split("/")
        if len(parts) != 2:
            return gt_string

        try:
            idx1 = int(parts[0])
            idx2 = int(parts[1])
            alleles = [ref] + alt.split(",")
            a1 = alleles[idx1] if idx1 < len(alleles) else "?"
            a2 = alleles[idx2] if idx2 < len(alleles) else "?"
            return f"{a1}/{a2}"
        except (ValueError, IndexError):
            return gt_string

    def get_variants_for_gene(self, gene: str, variants: List[Variant]) -> List[Variant]:
        """Filter variants for a specific pharmacogene."""
        gene_rsids = set(self.GENE_RSID_MAP.get(gene, {}).keys())
        if gene_rsids:
            rsid_hits = [v for v in variants if v.rsid in gene_rsids]
            if rsid_hits:
                return rsid_hits

        chrom = self.GENE_CHROMOSOME_MAP.get(gene)
        if not chrom:
            return []
        return [v for v in variants if str(v.chrom).lower().replace("chr", "") == chrom]

    def infer_diplotype(self, gene: str, variants: List[Variant]) -> str:
        """Infer a simplified diplotype from known variant alleles."""
        detected_alleles: List[str] = []

        for variant in variants:
            if variant.rsid not in self.RSID_TO_ALLELE:
                continue

            allele, _function = self.RSID_TO_ALLELE[variant.rsid]
            genotype = variant.genotype
            if "/" not in genotype:
                continue

            left, right = genotype.split("/", maxsplit=1)
            if left == variant.ref and right == variant.ref:
                continue
            detected_alleles.append(allele)

        if not detected_alleles:
            return "*1/*1"

        unique_alleles = sorted(set(detected_alleles))
        if len(unique_alleles) == 1:
            return f"{unique_alleles[0]}/{unique_alleles[0]}"
        return f"{unique_alleles[0]}/{unique_alleles[1]}"


def parse_vcf_file(vcf_content: str) -> List[Variant]:
    """Convenience function to parse VCF content."""
    parser = VCFParser()
    return parser.parse_vcf_content(vcf_content)


def extract_genes_from_vcf(vcf_content: str) -> Dict[str, List[Variant]]:
    """Extract variants grouped by supported genes."""
    parser = VCFParser()
    all_variants = parser.parse_vcf_content(vcf_content)

    gene_variants: Dict[str, List[Variant]] = {}
    for gene in ["CYP2D6", "CYP2C19", "CYP2C9", "SLCO1B1", "TPMT", "DPYD"]:
        gene_variants[gene] = parser.get_variants_for_gene(gene, all_variants)

    return gene_variants
