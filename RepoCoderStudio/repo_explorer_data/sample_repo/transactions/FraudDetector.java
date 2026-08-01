package transactions;

import java.util.List;
import java.time.LocalDateTime;
import java.time.temporal.ChronoUnit;

/**
 * Fraud detection heuristics for the demo BFSI sample repository.
 *
 * Java counterpart of transactions/fraud_detector.py -- same heuristics,
 * kept in step with the Python version so Stage 4/5 has a genuinely
 * bilingual repository to index rather than a Python-only demo.
 */
public class FraudDetector {

    /**
     * Compute a 0-100 fraud risk score for a transaction based on amount
     * and payee history.
     */
    public double calculateRiskScore(double amount, double accountAvgTransaction, boolean isNewPayee) {
        double score = 0.0;
        if (accountAvgTransaction > 0) {
            double ratio = amount / accountAvgTransaction;
            score += Math.min(ratio * 10, 60);
        }
        if (isNewPayee) {
            score += 25;
        }
        if (amount > 100000) {
            score += 15;
        }
        return Math.min(score, 100.0);
    }

    /**
     * Decide whether a transaction should be flagged for manual fraud
     * review.
     */
    public boolean flagSuspiciousTransaction(double riskScore, double threshold) {
        return riskScore >= threshold;
    }

    /**
     * Return true if too many transactions have occurred within a short
     * time window (velocity fraud check).
     */
    public boolean checkVelocityLimit(List<LocalDateTime> recentTransactionTimes, int windowMinutes, int maxCount) {
        if (recentTransactionTimes.isEmpty()) {
            return false;
        }
        LocalDateTime cutoff = LocalDateTime.now().minus(windowMinutes, ChronoUnit.MINUTES);
        int recentCount = 0;
        for (LocalDateTime t : recentTransactionTimes) {
            if (!t.isBefore(cutoff)) {
                recentCount++;
            }
        }
        return recentCount > maxCount;
    }

    /**
     * Flag a suspicious pattern of suspiciously round transaction
     * amounts, often seen in structuring/smurfing.
     */
    public boolean detectRoundAmountPattern(List<Double> amounts) {
        if (amounts.isEmpty()) {
            return false;
        }
        long roundCount = 0;
        for (double a : amounts) {
            if (a > 0 && a % 1000 == 0) {
                roundCount++;
            }
        }
        return ((double) roundCount / amounts.size()) > 0.6;
    }
}
