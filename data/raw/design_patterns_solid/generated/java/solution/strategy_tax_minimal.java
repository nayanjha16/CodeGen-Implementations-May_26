// DesignPatternsSolid | kind=design_pattern | label=strategy | domain=tax | tier=minimal
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
        return strategy.apply(amount);
    }
    public String tag() { return "tax-strategy"; }
}
