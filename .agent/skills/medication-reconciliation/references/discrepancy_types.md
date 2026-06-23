# Discrepancy Types

## omission
A medication present in one source is absent in another without documented justification.
Example: furosemide in the discharge summary but absent from the active prescription.

## duplication
The same medication appears under two different names (brand + generic) or in two separate entries.
Example: omeprazole prescribed and patient also buying "stomach protector" OTC.

## discontinued_medication_still_taken
The discharge summary or prescription indicates a medication was stopped, but the patient reports still taking it.
Example: ibuprofen listed as "avoid" at discharge, patient still taking 600 mg.

## new_medication_not_in_prescription
Patient reports taking a medication not present in the discharge summary or active prescription.
Example: patient taking a supplement or OTC drug not documented anywhere.

## dose_mismatch
The dose in one source differs from another without explanation.
Example: atenolol 50 mg in discharge summary, 25 mg in active prescription.

## frequency_mismatch
The frequency of administration differs across sources.
Example: furosemide "every morning" at discharge, "twice daily" in prescription.

## route_mismatch
The route of administration differs.
Example: insulin subcutaneous in discharge, no route specified in prescription.

## patient_uncertainty
The patient or caregiver is uncertain about a medication, its name, dose, or whether they are still taking it.
Example: patient reports "I think I take something for blood pressure but I'm not sure of the name."

## possible_allergy_issue
A medication is present in any list that matches or potentially matches a known allergy.
Example: penicillin prescribed, patient has documented penicillin allergy.

## high_risk_medication_issue
A medication classified as high-risk (anticoagulant, NSAID, diuretic, etc.) has any discrepancy.
Always classify as MEDIUM or HIGH risk.

## self_medication_or_otc_issue
Patient reports taking an OTC medication, supplement, or herbal product not documented in any clinical source.
Example: patient buying ibuprofen without prescription.
