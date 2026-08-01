package policies;

import java.util.Set;

/** Repository-specific cross-border transfer policy. */
public class TransferPolicy {
    /** Calculate the repository's 0-100 cross-border transfer risk score. */
    public double transferRiskScore(
        double amount,
        int customerTenureDays,
        String destinationCountry,
        boolean trustedDevice
    ) {
        Set<String> highRiskCountries = Set.of("IR", "KP", "SY");
        double score = 0.0;
        if (amount >= 250000) {
            score += 40;
        } else if (amount >= 100000) {
            score += 25;
        }
        if (customerTenureDays < 30) {
            score += 20;
        }
        if (highRiskCountries.contains(destinationCountry.trim().toUpperCase())) {
            score += 30;
        }
        if (!trustedDevice) {
            score += 15;
        }
        return Math.min(score, 100.0);
    }

    /** Require an additional authentication challenge at score 50 or above. */
    public boolean requiresStepUpAuth(double riskScore) {
        return riskScore >= 50.0;
    }

    /** Return this repository's daily transfer limit for an account tier. */
    public double dailyTransferLimit(String accountTier) {
        return switch (accountTier.trim().toUpperCase()) {
            case "STANDARD" -> 100000.0;
            case "PREMIUM" -> 500000.0;
            case "PRIVATE" -> 2000000.0;
            default -> 50000.0;
        };
    }
}
