// DesignPatternsSolid | kind=combo | label=strategy+ocp | domain=discount | tier=minimal
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
        return strategy.apply(amount);
    }
    public String tag() { return "discount-strategy"; }
}
