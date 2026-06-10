# Response to Subject-Matter-Expert Review
## Organizational Trust Quotient® (OTQ) — Capstone Project

**Team:** Vernon T. Cox · Srilatha Alla
**Program:** CNM Ingenuity Data Science Bootcamp
**Subject-Matter Expert:** Prof. Robert G. DelCampo, Ph.D. — Rutledge Professor of Management, Anderson School of Management, UNM
**Artifact updated:** OTQ_Working_Copy_v10.ipynb (code + embedded documentation)
**Date:** June 10, 2026

---

## Purpose

This document records the feedback provided by Prof. Robert G. DelCampo during his subject-matter-expert review of the OTQ capstone and maps each observation to the corresponding update made in version 10 of the project notebook. Prof. DelCampo assessed the work as well-constructed and disciplined, with a complete and defensible end-to-end pipeline. His feedback concentrated on a single, well-founded concern — the construct-validity bridge between what OTQ measures and what it claims — which the v10 revision addresses directly through reframing, a dedicated construct-validity treatment, and a runnable convergent-validity scaffold.

## Strengths Acknowledged (No Change Required)

Prof. DelCampo affirmed the following aspects of the project; these were retained unchanged in v10:

- A complete, defensible pipeline: multi-source ingestion, a normalized event schema, principled feature engineering, a justified modeling choice, and honest evaluation.
- A correct and well-stated argument for Ridge regression over ordinary least squares under multicollinearity.
- A thoughtful, privacy-by-design posture and a clever, reproducible benchmark fixture.
- Full coverage of the capstone rubric (Section 7).

## Comment-to-Update Crosswalk

Each row pairs an observation from the review with the specific change implemented in v10.

| Reviewer Observation — Prof. DelCampo | Update Implemented in v10 |
|---|---|
| **Construct-validity gap (the core issue):** OTQ adopts trust as a psychological disposition (Mayer, Davis & Schoorman, 1995) but operationalizes it through behavioral byproducts and validates against a behavioral proxy (median response time). The "trust" label is asserted by theoretical analogy rather than demonstrated (Cronbach & Meehl, 1955; MacKenzie et al., 2011). | The central claim is reframed across six cells: OTQ now directly measures communication engagement and predicts organizational responsiveness, with trust positioned as the theorized upstream construct — not a quantity measured directly. A new "What OTQ Measures — A Note on Construct Scope" section states this plainly, and a full "Construct Validity & Planned Convergent-Validity Study" section names the measurement framework (Cronbach & Meehl, 1955; MacKenzie et al., 2011). |
| To earn the word "trust," the OTQ score must converge with a validated trust or psychological-safety instrument (e.g., Edmondson's 1999 scale) administered to the same teams. | A convergent-validity protocol is documented: administer Edmondson's (1999) seven-item psychological-safety scale (and/or a Mayer-based trust scale), aggregate OTQ to the same team and window, and correlate (Pearson/Spearman) with a pre-registered positive prediction. A runnable scaffold cell operationalizes this and computes the correlation when survey data is supplied. |
| **Recommendation (a):** reframe the claim to a communication-engagement signal predictive of organizational responsiveness. | Implemented. All "trust signal" and "proxy for trust" wording was removed and replaced with "engagement weight," "responsiveness outcome," and explicit "theorized construct" framing in the overview, EU-scoring, feature-engineering, modeling, and summary sections. |
| **Recommendation (b):** add a small convergent-validity study correlating OTQ against a short validated trust/psychological-safety survey on at least one real team — the step that converts the trademark into a defensible construct. | Operationalized as a defined next step plus a non-fabricating scaffold cell. On the synthetic benchmark it reports that the criterion measure is absent and prints the exact protocol; with a real survey export it computes the convergent-validity correlation. No validity evidence is manufactured. |
| **Levels of analysis (Chan, 1998):** be explicit about the level at which the construct is measured and how individual signals compose to a team-level construct. | A new subsection notes that OTQ currently operates at the daily / team-aggregate level and calls for an explicit composition model (e.g., direct-consensus vs. referent-shift) when aggregating to the team level. Added as a planned next step. |
| **Common-method concern (Podsakoff et al., 2003):** predictors and outcome are both drawn from the same communication stream, which can inflate their association. | A new subsection acknowledges the shared-method dependency between the engagement features and the response-time outcome, and identifies the independent survey criterion as the remedy that breaks it. |
| Suggested literature to ground the construct-validity argument. | Four sources were added to the notebook references: Cronbach & Meehl (1955); MacKenzie, Podsakoff & Podsakoff (2011); Chan (1998); and Podsakoff et al. (2003). Mayer et al. (1995), Edmondson (1999), and Dirks & Ferrin (2002) were already cited. |

## Summary of New Material Added in v10

- **Scope note.** "What OTQ Measures — A Note on Construct Scope" distinguishes what is directly measured (engagement, responsiveness) from what is theorized (trust).
- **Construct-validity section.** A dedicated section covering the construct-validity question, the convergent-validity protocol, levels of analysis (Chan, 1998), and common-method variance (Podsakoff et al., 2003), with key references.
- **Convergent-validity scaffold.** A runnable cell that prints the validation protocol when no survey is present and computes the OTQ-vs-survey correlation when one is supplied — without fabricating evidence.
- **Strengthened limitations and next steps.** The summary now names the unvalidated label and lists the convergent-validity study and a levels-of-analysis composition model as concrete next steps.

## Open Item for Follow-Up

Of the three questions posed to the SME — construct validity, the inferential chain, and the ethics of behavioral measurement — the written review thoroughly addressed the first two (his answer to the "weakest link" question is the metadata-to-trust leap above). The third question, on whether the privacy guardrails meet corporate standards, was not substantively addressed in this reply and is planned as a brief, targeted follow-up.

For consistency, the same construct-validity reframing is queued for the capstone proposal document so that the proposal and notebook present a single, aligned claim.

## References Added or Reaffirmed

- Chan, D. (1998). Functional relations among constructs in the same content domain at different levels of analysis: A typology of composition models. *Journal of Applied Psychology, 83*(2), 234–246.
- Cronbach, L. J., & Meehl, P. E. (1955). Construct validity in psychological tests. *Psychological Bulletin, 52*(4), 281–302.
- Dirks, K. T., & Ferrin, D. L. (2002). Trust in leadership: Meta-analytic findings and implications for research and practice. *Journal of Applied Psychology, 87*(4), 611–628.
- Edmondson, A. (1999). Psychological safety and learning behavior in work teams. *Administrative Science Quarterly, 44*(2), 350–383.
- MacKenzie, S. B., Podsakoff, P. M., & Podsakoff, N. P. (2011). Construct measurement and validation procedures in MIS and behavioral research. *MIS Quarterly, 35*(2), 293–334.
- Mayer, R. C., Davis, J. H., & Schoorman, F. D. (1995). An integrative model of organizational trust. *Academy of Management Review, 20*(3), 709–734.
- Podsakoff, P. M., MacKenzie, S. B., Lee, J.-Y., & Podsakoff, N. P. (2003). Common method biases in behavioral research: A critical review of the literature and recommended remedies. *Journal of Applied Psychology, 88*(5), 879–903.

---

*Prepared by Vernon T. Cox and Srilatha Alla · CNM Ingenuity Data Science Bootcamp · OTQ Capstone Project*

*The Organizational Trust Quotient® is a proprietary and trademarked methodology. All scoring logic, lexicon design, and interpretive frameworks remain the intellectual property of Vernon T. Cox.*
