# Expected output — case_002 diuretic omission

## What the agent should detect

**Discrepancy type:** Drug omitted from active prescription (addition in discharge, absent from GP record)  
**Medication involved:** Furosemide 40 mg  
**Risk level:** HIGH  

## What to say during the demo

> "The discharge summary clearly prescribes furosemide — a diuretic critical
> for fluid management in heart failure. But the GP prescription that was
> actually dispensed to the patient? Furosemide is missing. It was never
> added to the system."

> "The patient didn't notice. He went home without the diuretic, and 10 days
> later he's presenting with ankle oedema and shortness of breath — classic
> decompensation symptoms."

> "Risk: HIGH. This is a transcription error at the care transition point —
> exactly the kind of error medication reconciliation is designed to catch."

## Key talking point

This case illustrates the most common and dangerous reconciliation gap: a drug
that was prescribed at discharge but never made it onto the GP prescription.
The patient couldn't know. Neither could the pharmacist. Only by comparing all
three sources does the gap become visible.

## What NOT to expect

The patient summary will NOT say:
- "You need furosemide"
- "Your prescription is incomplete"
- "Contact your doctor immediately"

The Policy Server blocks all directives. The output will say there may be a
question about your medication list — please review it with your GP or pharmacist.
