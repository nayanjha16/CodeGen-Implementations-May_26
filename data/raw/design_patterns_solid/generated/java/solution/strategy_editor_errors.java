// DesignPatternsSolid | kind=design_pattern | label=strategy | domain=editor | tier=errors
package org.example.patterns;

interface EditorStrategy {
    int apply(int amount);
}

class EditorNormalStrategy implements EditorStrategy {
    public int apply(int amount) { return amount; }
}

class EditorDiscountStrategy implements EditorStrategy {
    public int apply(int amount) { return amount / 2; }
}

public class EditorContext {
    private EditorStrategy strategy;
    public EditorContext(EditorStrategy strategy) { this.strategy = strategy; }
    public void setStrategy(EditorStrategy strategy) { this.strategy = strategy; }
    public int execute(int amount) {
        if (amount < 0) throw new IllegalArgumentException("amount >= 0");
        return strategy.apply(amount);
    }
    public String tag() { return "editor-strategy"; }
}
