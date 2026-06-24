# Expected output — case_001 NSAID + anticoagulant

## What the agent should detect

**Discrepancy type:** Drug still taken after discontinuation at discharge  
**Medications involved:** Ibuprofen 600 mg (NSAID) + Apixaban 5 mg (anticoagulant)  
**Risk level:** HIGH  

## What to say during the demo

> "The agent found it: ibuprofen was discontinued at hospital discharge — it's
> right there in the discharge summary — but the patient reported taking it 3 to
> 4 times a week for knee pain. She bought it over the counter and didn't
> connect it to her blood thinner."

> "Risk level: HIGH. The professional checklist flags this as an urgent
> anticoagulant + NSAID interaction. The patient summary says there may be a
> question about one of your medications — please confirm with your GP or
> pharmacist. No prescriptive language."

## Key talking point

This case demonstrates why reconciliation matters: the hospital, the GP record,
and the patient's own account all told a different story. The agent compared
all three, found the gap, and surfaced it for professional review — without
ever prescribing or telling the patient what to do.

## What NOT to expect

The patient summary will NOT say:
- "Stop taking ibuprofen"
- "It is dangerous to continue"
- "You should take paracetamol instead"

The Policy Server blocks all prescriptive language. This is deliberate.
