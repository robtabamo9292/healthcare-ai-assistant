"""
Healthcare AI Assistant — Clinical Workflow Demo
Built with Anthropic Claude API

Simulates the kind of AI assistant a Business Analyst would configure
and deploy for a health system client using a platform like Qualified Health.

Use case: Heart failure patient review assistant
- Takes a mock patient summary as input
- Returns a structured clinical recommendation for physician review
- Demonstrates prompt engineering, safety guardrails, and traceable output

Author: Robert Tabamo
"""

import anthropic
import json
import os
from datetime import datetime


# ── System Prompt ──────────────────────────────────────────────────────────────
# This is the core of the assistant — engineered to mirror real clinical
# workflow requirements: specificity, safety, traceability, human oversight.

SYSTEM_PROMPT = """
You are a clinical decision support assistant for cardiologists at a major health system.
Your role is to help identify heart failure patients who may benefit from optimized
guideline-directed medical therapy (GDMT) based on current ACC/AHA guidelines.

When reviewing a patient summary, you must:

1. SUMMARIZE the patient's current HF medications and dosages
2. COMPARE against current ACC/AHA heart failure guidelines for HFrEF
3. FLAG any gaps or suboptimal dosing with specific guideline references
4. CITE the exact data point from the patient record that supports each observation
5. RECOMMEND next steps for the cardiologist to review

OUTPUT FORMAT:
Return a structured JSON response with the following fields:
- patient_id: string
- review_date: string (today's date)
- medications_summary: list of current HF medications
- guideline_gaps: list of identified gaps (each with: finding, guideline_reference, source_data)
- optimization_opportunities: list of specific recommendations
- priority_level: "HIGH" | "MEDIUM" | "LOW"
- clinician_note: brief plain-language summary for the cardiologist
- disclaimer: always include "For physician review only. Not a clinical decision."

RULES:
- Never make a clinical decision — always frame output as "for physician review"
- If data is missing or unclear, explicitly state what is missing — do not infer
- Only reference data that is present in the patient summary
- Flag if any data is older than 90 days
- Use standard clinical terminology appropriate for a cardiologist audience
"""


# ── Mock Patient Data ──────────────────────────────────────────────────────────
# In a real deployment this would pull from an EHR integration.
# Here we use structured mock data to demonstrate the workflow.

MOCK_PATIENTS = [
    {
        "patient_id": "PT-001",
        "name": "James R. (de-identified)",
        "age": 67,
        "diagnosis": "HFrEF, EF 32%",
        "comorbidities": ["Type 2 Diabetes", "CKD Stage 2 (eGFR 64)", "Hypertension"],
        "current_medications": [
            {"name": "Carvedilol", "dose": "6.25mg", "frequency": "BID", "last_updated": "2025-01-10"},
            {"name": "Lisinopril", "dose": "5mg", "frequency": "daily", "last_updated": "2025-01-10"},
            {"name": "Furosemide", "dose": "40mg", "frequency": "daily", "last_updated": "2025-01-10"},
        ],
        "recent_labs": {
            "BNP": "420 pg/mL (2025-01-05)",
            "Creatinine": "1.4 mg/dL (2025-01-05)",
            "Potassium": "4.2 mEq/L (2025-01-05)",
            "eGFR": "64 mL/min (2025-01-05)"
        },
        "vitals": {
            "BP": "118/72 mmHg",
            "HR": "68 bpm",
            "date": "2025-01-10"
        },
        "last_echo": "EF 32%, dated 2024-10-15"
    },
    {
        "patient_id": "PT-002",
        "name": "Maria S. (de-identified)",
        "age": 58,
        "diagnosis": "HFrEF, EF 28%",
        "comorbidities": ["Type 2 Diabetes", "Hypertension"],
        "current_medications": [
            {"name": "Metoprolol Succinate", "dose": "50mg", "frequency": "daily", "last_updated": "2024-11-20"},
            {"name": "Sacubitril/Valsartan", "dose": "24/26mg", "frequency": "BID", "last_updated": "2024-11-20"},
            {"name": "Furosemide", "dose": "20mg", "frequency": "daily", "last_updated": "2024-11-20"},
        ],
        "recent_labs": {
            "BNP": "890 pg/mL (2024-10-01)",
            "Creatinine": "1.1 mg/dL (2024-10-01)",
            "Potassium": "3.9 mEq/L (2024-10-01)",
            "eGFR": "72 mL/min (2024-10-01)"
        },
        "vitals": {
            "BP": "132/80 mmHg",
            "HR": "74 bpm",
            "date": "2024-11-20"
        },
        "last_echo": "EF 28%, dated 2024-09-10"
    }
]


# ── Assistant Logic ────────────────────────────────────────────────────────────

def review_patient(patient: dict) -> dict:
    """
    Send a patient summary to Claude for clinical review.
    Returns structured JSON output for physician review.
    """
    client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

    patient_summary = f"""
    Please review the following heart failure patient for GDMT optimization opportunities.

    PATIENT SUMMARY:
    {json.dumps(patient, indent=2)}

    Today's date: {datetime.now().strftime('%Y-%m-%d')}
    """

    print(f"\n{'='*60}")
    print(f"Reviewing patient: {patient['patient_id']}")
    print(f"{'='*60}")

    message = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=1500,
        system=SYSTEM_PROMPT,
        messages=[
            {"role": "user", "content": patient_summary}
        ]
    )

    response_text = message.content[0].text

    # Parse JSON response
    try:
        # Strip markdown code fences if present
        clean = response_text.replace("```json", "").replace("```", "").strip()
        result = json.loads(clean)
    except json.JSONDecodeError:
        result = {"raw_response": response_text, "parse_error": "Could not parse JSON"}

    return result


def run_population_review(patients: list) -> list:
    """
    Run review across a list of patients.
    In production this would process thousands of patients from EHR data.
    """
    results = []
    high_priority = []

    for patient in patients:
        result = review_patient(patient)
        results.append(result)

        if result.get("priority_level") == "HIGH":
            high_priority.append(result.get("patient_id"))

        # Print formatted output
        print(f"\nPATIENT: {result.get('patient_id', 'Unknown')}")
        print(f"PRIORITY: {result.get('priority_level', 'Unknown')}")
        print(f"NOTE: {result.get('clinician_note', 'N/A')}")

        gaps = result.get("guideline_gaps", [])
        if gaps:
            print(f"\nGaps identified ({len(gaps)}):")
            for gap in gaps:
                print(f"  • {gap.get('finding', '')}")
                print(f"    Reference: {gap.get('guideline_reference', '')}")

        print(f"\nDISCLAIMER: {result.get('disclaimer', '')}")

    print(f"\n{'='*60}")
    print(f"POPULATION SUMMARY")
    print(f"{'='*60}")
    print(f"Patients reviewed: {len(results)}")
    print(f"High priority: {len(high_priority)} — {high_priority}")

    return results


# ── Entry Point ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("Healthcare AI Assistant — Heart Failure GDMT Review")
    print("Powered by Anthropic Claude")
    print("For demonstration purposes only\n")

    results = run_population_review(MOCK_PATIENTS)

    # Save results to JSON for review
    output_file = f"review_output_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)

    print(f"\nFull results saved to: {output_file}")
