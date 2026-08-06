// DesignPatternsSolid | kind=combo | label=strategy+ocp | domain=session | tier=errors
package org.example.patterns;

interface SessionStrategy {
    int apply(int amount);
}

class SessionNormalStrategy implements SessionStrategy {
    public int apply(int amount) { return amount; }
}

class SessionDiscountStrategy implements SessionStrategy {
    public int apply(int amount) { return amount / 2; }
}

public class SessionContext {
    private SessionStrategy strategy;
    public SessionContext(SessionStrategy strategy) { this.strategy = strategy; }
    public void setStrategy(SessionStrategy strategy) { this.strategy = strategy; }
    public int execute(int amount) {
        if (amount < 0) throw new IllegalArgumentException("amount >= 0");
        return strategy.apply(amount);
    }
    public String tag() { return "session-strategy"; }
}
