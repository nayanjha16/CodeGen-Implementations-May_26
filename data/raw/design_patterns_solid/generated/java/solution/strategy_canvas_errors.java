// DesignPatternsSolid | kind=design_pattern | label=strategy | domain=canvas | tier=errors
package org.example.patterns;

interface CanvasStrategy {
    int apply(int amount);
}

class CanvasNormalStrategy implements CanvasStrategy {
    public int apply(int amount) { return amount; }
}

class CanvasDiscountStrategy implements CanvasStrategy {
    public int apply(int amount) { return amount / 2; }
}

public class CanvasContext {
    private CanvasStrategy strategy;
    public CanvasContext(CanvasStrategy strategy) { this.strategy = strategy; }
    public void setStrategy(CanvasStrategy strategy) { this.strategy = strategy; }
    public int execute(int amount) {
        if (amount < 0) throw new IllegalArgumentException("amount >= 0");
        return strategy.apply(amount);
    }
    public String tag() { return "canvas-strategy"; }
}
