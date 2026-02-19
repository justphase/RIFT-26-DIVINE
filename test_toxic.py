import requests
import json

# Read VCF file
with open('data/toxic_result.vcf', 'r') as f:
    vcf_content = f.read()

# Prepare payload
payload = {
    "vcf_content": vcf_content,
    "drug": "CLOPIDOGREL",
    "patient_id": "PATIENT_TOXIC",
    "use_llm": False
}

# Send request
response = requests.post("http://localhost:8000/analyze/json", json=payload)

# Print result
print("Status Code:", response.status_code)
print("\nResponse:")
print(json.dumps(response.json(), indent=2))
