package accounts;

import java.util.HashMap;
import java.util.Map;

/**
 * Customer identity verification (KYC) for the demo BFSI sample repository.
 *
 * Java counterpart of accounts/kyc_validator.py -- same checks, kept in
 * step with the Python version so Stage 4/5 has a genuinely bilingual
 * repository to index rather than a Python-only demo.
 */
public class KycValidator {

    /**
     * Check whether a string matches the Indian PAN card format (5
     * letters, 4 digits, 1 letter).
     */
    public boolean validatePan(String panNumber) {
        String normalized = panNumber.trim().toUpperCase();
        return normalized.matches("[A-Z]{5}[0-9]{4}[A-Z]{1}");
    }

    /**
     * Check whether a string is a plausible 12-digit Aadhaar number.
     */
    public boolean validateAadhaar(String aadhaarNumber) {
        String digits = aadhaarNumber.replace(" ", "");
        return digits.matches("[0-9]+") && digits.length() == 12;
    }

    /**
     * Run full KYC identity verification, combining PAN and Aadhaar
     * checks.
     */
    public Map<String, Boolean> verifyIdentity(String panNumber, String aadhaarNumber, String fullName) {
        boolean panOk = validatePan(panNumber);
        boolean aadhaarOk = validateAadhaar(aadhaarNumber);
        boolean nameOk = fullName != null && !fullName.trim().isEmpty();

        Map<String, Boolean> result = new HashMap<>();
        result.put("verified", panOk && aadhaarOk && nameOk);
        result.put("panValid", panOk);
        result.put("aadhaarValid", aadhaarOk);
        result.put("nameProvided", nameOk);
        return result;
    }

    /**
     * Mask a PAN number for display, keeping only the last 4 characters
     * visible.
     */
    public String maskPan(String panNumber) {
        String normalized = panNumber.trim().toUpperCase();
        if (normalized.length() < 4) {
            return "*".repeat(normalized.length());
        }
        String visible = normalized.substring(normalized.length() - 4);
        return "*".repeat(normalized.length() - 4) + visible;
    }
}
