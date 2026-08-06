// DesignPatternsSolid | kind=combo | label=strategy+ocp | domain=billing | tier=minimal
package org.example.patterns;

interface BillingStrategy {
    int apply(int amount);
}

class BillingNormalStrategy implements BillingStrategy {
    public int apply(int amount) { return amount; }
}

class BillingDiscountStrategy implements BillingStrategy {
    public int apply(int amount) { return amount / 2; }
}

public class BillingContext {
    private BillingStrategy strategy;
    public BillingContext(BillingStrategy strategy) { this.strategy = strategy; }
    public void setStrategy(BillingStrategy strategy) { this.strategy = strategy; }
    public int execute(int amount) {
        return strategy.apply(amount);
    }
    public String tag() { return "billing-strategy"; }
}
