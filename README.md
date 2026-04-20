# Healthcare AI Assistant: Heart Failure GDMT Review

A clinical decision support tool built with the Anthropic Claude API that identifies heart failure patients with opportunities for improved guideline-directed medical therapy (GDMT).

---

## What it does

- Takes structured patient summaries as input (medications, labs, vitals, echo results)
- Applies ACC/AHA heart failure guidelines to identify GDMT gaps
- Returns a structured JSON output with prioritized findings and guideline citations
- Flags missing or outdated data rather than inferring
- Designed with human oversight built in — all outputs are for physician review only

---

## Why I built this

The Business Analyst role at a healthcare AI company involves configuring AI assistants for specific clinical workflows. This project simulates that process end-to-end:

1. **Use case discovery** — identifying a high-value clinical problem (GDMT gaps in heart failure)
2. **Prompt engineering** — writing a system prompt that constrains the AI to safe, traceable output
3. **Evaluation** — structuring output so clinicians can verify each finding against source data
4. **Governance** — building in explicit disclaimers and human review requirements

---

## How it works

```
patient summary (mock EHR data)
        ↓
  Claude API (claude-opus-4-5)
        ↓
  structured JSON output
        ↓
  clinician review queue
```

The system prompt enforces:
- Citation of source data for every finding
- Explicit flagging of missing or stale data (>90 days)
- JSON output format for downstream workflow integration
- Hard disclaimer on every response: "For physician review only"

---

## Sample output

```json
{
  "patient_id": "PT-001",
  "priority_level": "HIGH",
  "guideline_gaps": [
    {
      "finding": "Carvedilol dose (6.25mg BID) is below target dose per ACC/AHA guidelines",
      "guideline_reference": "ACC/AHA 2022 HF Guidelines — target carvedilol dose 25mg BID for HFrEF",
      "source_data": "Current medications: Carvedilol 6.25mg BID (updated 2025-01-10)"
    },
    {
      "finding": "No SGLT2 inhibitor prescribed despite Class I indication in HFrEF with DM2",
      "guideline_reference": "ACC/AHA 2022 HF Guidelines — SGLT2i recommended for all HFrEF patients",
      "source_data": "Diagnosis: HFrEF EF 32%, Comorbidities: Type 2 Diabetes"
    }
  ],
  "clinician_note": "Patient PT-001 has two optimization opportunities: beta-blocker titration and addition of SGLT2 inhibitor. eGFR 64 supports SGLT2i use. BP and HR suggest hemodynamic tolerance for uptitration.",
  "disclaimer": "For physician review only. Not a clinical decision."
}
```

---

## Setup

```bash
# Clone the repo
git clone https://github.com/robtabamo9292/healthcare-ai-assistant
cd healthcare-ai-assistant

# Install dependencies
pip install -r requirements.txt

# Set your API key
export ANTHROPIC_API_KEY=your_key_here

# Run the demo
python assistant.py
```

---

## Project structure

```
healthcare-ai-assistant/
├── assistant.py          # Main assistant logic and Claude API integration
├── requirements.txt      # Python dependencies
└── README.md             # This file
```

---

## Key design decisions

**Why JSON output?**
Structured output integrates directly into clinical workflows — a JSON response can be rendered in a clinician dashboard, stored in an audit log, or trigger downstream actions without manual parsing.

**Why explicit source citation?**
Healthcare AI requires traceability. Every finding must be linkable back to a specific data point in the patient record. This is a core requirement of safe clinical AI deployment.

**Why mock data?**
This is a demonstration project. In production, patient data would flow from EHR integrations (Epic, Oracle Health) through a HIPAA-compliant data layer. No real PHI is used here.

---

Built by [Robert Tabamo](https://linkedin.com/in/roberttabamo)
