// DesignPatternsSolid | kind=design_pattern | label=strategy | domain=analytics | tier=logging
package org.example.patterns;

interface AnalyticsStrategy {
    int apply(int amount);
}

class AnalyticsNormalStrategy implements AnalyticsStrategy {
    public int apply(int amount) { return amount; }
}

class AnalyticsDiscountStrategy implements AnalyticsStrategy {
    public int apply(int amount) { return amount / 2; }
}

public class AnalyticsContext {
    private AnalyticsStrategy strategy;
    public AnalyticsContext(AnalyticsStrategy strategy) { this.strategy = strategy; }
    public void setStrategy(AnalyticsStrategy strategy) { this.strategy = strategy; }
    public int execute(int amount) {
        return strategy.apply(amount);
    }
    public String tag() { return "analytics-strategy"; }
}
