// DesignPatternsSolid | kind=design_pattern | label=strategy | domain=widgets | tier=minimal
package org.example.patterns;

interface WidgetsStrategy {
    int apply(int amount);
}

class WidgetsNormalStrategy implements WidgetsStrategy {
    public int apply(int amount) { return amount; }
}

class WidgetsDiscountStrategy implements WidgetsStrategy {
    public int apply(int amount) { return amount / 2; }
}

public class WidgetsContext {
    private WidgetsStrategy strategy;
    public WidgetsContext(WidgetsStrategy strategy) { this.strategy = strategy; }
    public void setStrategy(WidgetsStrategy strategy) { this.strategy = strategy; }
    public int execute(int amount) {
        return strategy.apply(amount);
    }
    public String tag() { return "widgets-strategy"; }
}
