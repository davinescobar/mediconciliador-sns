# Expected output — case_003 PPI brand/generic duplication

## What the agent should detect

**Discrepancy type:** Duplication — same drug under two different names  
**Medications involved:** Omeprazole 20 mg (prescription) + stomach protector OTC (generic omeprazole)  
**Risk level:** LOW  

## What to say during the demo

> "This case shows a different kind of error — duplication. The hospital
> prescribed omeprazole. The patient has also been buying a generic 'stomach
> protector' from the pharmacy for years. She thinks they're different because
> the capsule colours are different. They're not — both are omeprazole 20 mg."

> "Low risk — doubling a PPI is not acutely dangerous — but it's unnecessary
> polypharmacy, it costs money, and it can cause side effects over time.
> This is the kind of thing a human clinician might miss in a 10-minute appointment."

## Key talking point

This case shows that reconciliation is not just about missing drugs or dangerous
interactions — it also catches redundancy. The agent normalises brand names to
generics and compares. 'Stomach protector' + omeprazole → duplication detected.

## Contrast with case_001

Use this case after case_001 to show the system handles the full spectrum of
severity: from HIGH (anticoagulant + NSAID) to LOW (PPI duplication).
This range demonstrates clinical completeness, not just emergency detection.
