// DesignPatternsSolid | kind=design_pattern | label=strategy | domain=scheduling | tier=logging
package org.example.patterns;

interface SchedulingStrategy {
    int apply(int amount);
}

class SchedulingNormalStrategy implements SchedulingStrategy {
    public int apply(int amount) { return amount; }
}

class SchedulingDiscountStrategy implements SchedulingStrategy {
    public int apply(int amount) { return amount / 2; }
}

public class SchedulingContext {
    private SchedulingStrategy strategy;
    public SchedulingContext(SchedulingStrategy strategy) { this.strategy = strategy; }
    public void setStrategy(SchedulingStrategy strategy) { this.strategy = strategy; }
    public int execute(int amount) {
        return strategy.apply(amount);
    }
    public String tag() { return "scheduling-strategy"; }
}
