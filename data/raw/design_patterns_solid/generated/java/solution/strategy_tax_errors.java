// DesignPatternsSolid | kind=design_pattern | label=strategy | domain=tax | tier=errors
package org.example.patterns;

interface TaxStrategy {
    int apply(int amount);
}

class TaxNormalStrategy implements TaxStrategy {
    public int apply(int amount) { return amount; }
}

class TaxDiscountStrategy implements TaxStrategy {
    public int apply(int amount) { return amount / 2; }
}

public class TaxContext {
    private TaxStrategy strategy;
    public TaxContext(TaxStrategy strategy) { this.strategy = strategy; }
    public void setStrategy(TaxStrategy strategy) { this.strategy = strategy; }
    public int execute(int amount) {
        if (amount < 0) throw new IllegalArgumentException("amount >= 0");
        return strategy.apply(amount);
    }
    public String tag() { return "tax-strategy"; }
}
