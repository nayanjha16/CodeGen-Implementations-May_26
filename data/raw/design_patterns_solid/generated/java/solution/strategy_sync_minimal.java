// DesignPatternsSolid | kind=design_pattern | label=strategy | domain=sync | tier=minimal
package org.example.patterns;

interface SyncStrategy {
    int apply(int amount);
}

class SyncNormalStrategy implements SyncStrategy {
    public int apply(int amount) { return amount; }
}

class SyncDiscountStrategy implements SyncStrategy {
    public int apply(int amount) { return amount / 2; }
}

public class SyncContext {
    private SyncStrategy strategy;
    public SyncContext(SyncStrategy strategy) { this.strategy = strategy; }
    public void setStrategy(SyncStrategy strategy) { this.strategy = strategy; }
    public int execute(int amount) {
        return strategy.apply(amount);
    }
    public String tag() { return "sync-strategy"; }
}
