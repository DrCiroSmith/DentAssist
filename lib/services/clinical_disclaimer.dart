/// Standardized AMA / ADA Clinical Decision Support (CDS) compliance metadata.
class ClinicalDisclaimer {
  static const String adaDisclaimerText =
      "DentAssist provides clinical decision support intended solely to augment, not replace, "
      "independent diagnostic assessment by a licensed dentist. Interpretations, differentials, "
      "and protocol recommendations are generated locally via on-device machine learning (MedGemma 4B) "
      "and must be verified through clinical examination, patient history, and diagnostic radiography.";

  static const String fdaCdsExemptionStatement =
      "Adheres to FDA 2022 Clinical Decision Support Guidance Section 520(o)(1)(E) for non-device software functions.";

  final DateTime timestamp;
  final String practitionerId;
  final bool hasAcceptedDisclaimer;

  ClinicalDisclaimer({
    required this.timestamp,
    required this.practitionerId,
    required this.hasAcceptedDisclaimer,
  });

  Map<String, dynamic> toAuditLog() {
    return {
      "audit_timestamp": timestamp.toIso8601String(),
      "practitioner_id": practitionerId,
      "disclaimer_accepted": hasAcceptedDisclaimer,
      "fda_cds_guidance": "520(o)(1)(E)",
      "ada_guidance_acknowledged": true,
      "inference_location": "LOCAL_AIR_GAPPED_MOBILE_RUNTIME",
    };
  }
}
