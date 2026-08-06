// DesignPatternsSolid | kind=design_pattern | label=strategy | domain=todo | tier=errors
package org.example.patterns;

interface TodoStrategy {
    int apply(int amount);
}

class TodoNormalStrategy implements TodoStrategy {
    public int apply(int amount) { return amount; }
}

class TodoDiscountStrategy implements TodoStrategy {
    public int apply(int amount) { return amount / 2; }
}

public class TodoContext {
    private TodoStrategy strategy;
    public TodoContext(TodoStrategy strategy) { this.strategy = strategy; }
    public void setStrategy(TodoStrategy strategy) { this.strategy = strategy; }
    public int execute(int amount) {
        if (amount < 0) throw new IllegalArgumentException("amount >= 0");
        return strategy.apply(amount);
    }
    public String tag() { return "todo-strategy"; }
}
