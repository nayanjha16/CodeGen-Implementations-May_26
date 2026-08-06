// DesignPatternsSolid | kind=combo | label=strategy+ocp | domain=editor | tier=minimal
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
        return strategy.apply(amount);
    }
    public String tag() { return "editor-strategy"; }
}
