# Fake Demo Documents

Synthetic clinical documents for demonstrating Tab 6 "New Case" in the
MediConciliador SNS Streamlit app.

All data is entirely fictional. No real patient information. Created for
the Kaggle Vibe Coding Agents Capstone demo.

---

## How to use during the demo

1. Open the app: `streamlit run app.py`
2. Click **Tab 6 — New Case**
3. For each of the three fields, copy the corresponding `.txt` file content
   and paste it (or use "Upload file" to upload the `.txt` directly).
4. Click **Extract & Analyze**
5. The LLM extracts medication data from the free text → deterministic pipeline
   detects discrepancies → Policy Server validates the output.

---

## Cases

### case_001 — NSAID + anticoagulant (MAIN VIDEO CASE)
```
demo/fake_documents/case_001_nsaid_anticoagulant/
├── 01_discharge_summary.txt     ← paste into "Discharge Summary"
├── 02_active_prescription.txt   ← paste into "Active Prescription"
├── 03_patient_interview.txt     ← paste into "Patient Interview"
└── expected_output.md           ← what the agent should detect
```
**Expected discrepancy:** Ibuprofen 600 mg — still taken by patient, discontinued at discharge.  
**Risk:** HIGH — NSAID + anticoagulant (apixaban) interaction.  
**Demo use:** PRIMARY — use this case in the video.

---

### case_002 — Diuretic omission at discharge
```
demo/fake_documents/case_002_diuretic_omission/
├── 01_discharge_summary.txt
├── 02_active_prescription.txt
├── 03_patient_interview.txt
└── expected_output.md
```
**Expected discrepancy:** Furosemide 40 mg — in discharge summary, absent from active prescription and patient report.  
**Risk:** HIGH — missing diuretic in a heart failure patient.  
**Demo use:** SECONDARY — good alternative case if time allows, or for screenshots.

---

### case_003 — Brand/generic PPI duplication
```
demo/fake_documents/case_003_ppi_duplication/
├── 01_discharge_summary.txt
├── 02_active_prescription.txt
├── 03_patient_interview.txt
└── expected_output.md
```
**Expected discrepancy:** Omeprazole 20 mg (prescription) duplicated by OTC "stomach protector" (same drug, different brand).  
**Risk:** LOW — unnecessary polypharmacy, no acute danger.  
**Demo use:** Use to contrast with HIGH-risk cases and show the system handles the full severity spectrum.

---

## Why these documents work

The documents are designed to be realistic enough that Gemini (the LLM used in
Tab 6's extraction step) can parse them correctly. Key design choices:

- Drug names are spelled out clearly (both brand and generic where relevant).
- Doses and frequencies are explicit.
- The discrepancy is embedded naturally in the patient interview — not obvious
  unless you compare all three sources.
- Documents are marked `[SYNTHETIC / DEMO DATA]` at the top to prevent any
  risk of being confused with real clinical records.

The `expected_output.md` in each folder explains what to say during the demo.
