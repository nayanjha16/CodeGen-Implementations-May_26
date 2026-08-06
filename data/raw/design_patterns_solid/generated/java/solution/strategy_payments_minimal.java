// DesignPatternsSolid | kind=design_pattern | label=strategy | domain=payments | tier=minimal
package org.example.patterns;

interface PaymentsStrategy {
    int apply(int amount);
}

class PaymentsNormalStrategy implements PaymentsStrategy {
    public int apply(int amount) { return amount; }
}

class PaymentsDiscountStrategy implements PaymentsStrategy {
    public int apply(int amount) { return amount / 2; }
}

public class PaymentsContext {
    private PaymentsStrategy strategy;
    public PaymentsContext(PaymentsStrategy strategy) { this.strategy = strategy; }
    public void setStrategy(PaymentsStrategy strategy) { this.strategy = strategy; }
    public int execute(int amount) {
        return strategy.apply(amount);
    }
    public String tag() { return "payments-strategy"; }
}
