// DesignPatternsSolid | kind=design_pattern | label=strategy | domain=backup | tier=errors
package org.example.patterns;

interface BackupStrategy {
    int apply(int amount);
}

class BackupNormalStrategy implements BackupStrategy {
    public int apply(int amount) { return amount; }
}

class BackupDiscountStrategy implements BackupStrategy {
    public int apply(int amount) { return amount / 2; }
}

public class BackupContext {
    private BackupStrategy strategy;
    public BackupContext(BackupStrategy strategy) { this.strategy = strategy; }
    public void setStrategy(BackupStrategy strategy) { this.strategy = strategy; }
    public int execute(int amount) {
        if (amount < 0) throw new IllegalArgumentException("amount >= 0");
        return strategy.apply(amount);
    }
    public String tag() { return "backup-strategy"; }
}
