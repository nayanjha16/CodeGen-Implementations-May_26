// DesignPatternsSolid | kind=combo | label=strategy+ocp | domain=email | tier=errors
package org.example.patterns;

interface EmailStrategy {
    int apply(int amount);
}

class EmailNormalStrategy implements EmailStrategy {
    public int apply(int amount) { return amount; }
}

class EmailDiscountStrategy implements EmailStrategy {
    public int apply(int amount) { return amount / 2; }
}

public class EmailContext {
    private EmailStrategy strategy;
    public EmailContext(EmailStrategy strategy) { this.strategy = strategy; }
    public void setStrategy(EmailStrategy strategy) { this.strategy = strategy; }
    public int execute(int amount) {
        if (amount < 0) throw new IllegalArgumentException("amount >= 0");
        return strategy.apply(amount);
    }
    public String tag() { return "email-strategy"; }
}
