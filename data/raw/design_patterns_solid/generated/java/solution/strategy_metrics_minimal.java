// DesignPatternsSolid | kind=design_pattern | label=strategy | domain=metrics | tier=minimal
package org.example.patterns;

interface MetricsStrategy {
    int apply(int amount);
}

class MetricsNormalStrategy implements MetricsStrategy {
    public int apply(int amount) { return amount; }
}

class MetricsDiscountStrategy implements MetricsStrategy {
    public int apply(int amount) { return amount / 2; }
}

public class MetricsContext {
    private MetricsStrategy strategy;
    public MetricsContext(MetricsStrategy strategy) { this.strategy = strategy; }
    public void setStrategy(MetricsStrategy strategy) { this.strategy = strategy; }
    public int execute(int amount) {
        return strategy.apply(amount);
    }
    public String tag() { return "metrics-strategy"; }
}
