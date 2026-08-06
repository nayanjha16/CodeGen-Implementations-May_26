// DesignPatternsSolid | kind=design_pattern | label=strategy | domain=discount | tier=errors
package org.example.patterns;

interface DiscountStrategy {
    int apply(int amount);
}

class DiscountNormalStrategy implements DiscountStrategy {
    public int apply(int amount) { return amount; }
}

class DiscountDiscountStrategy implements DiscountStrategy {
    public int apply(int amount) { return amount / 2; }
}

public class DiscountContext {
    private DiscountStrategy strategy;
    public DiscountContext(DiscountStrategy strategy) { this.strategy = strategy; }
    public void setStrategy(DiscountStrategy strategy) { this.strategy = strategy; }
    public int execute(int amount) {
        if (amount < 0) throw new IllegalArgumentException("amount >= 0");
        return strategy.apply(amount);
    }
    public String tag() { return "discount-strategy"; }
}
