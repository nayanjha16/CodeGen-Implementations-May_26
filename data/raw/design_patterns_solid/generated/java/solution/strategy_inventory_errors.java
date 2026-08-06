// DesignPatternsSolid | kind=design_pattern | label=strategy | domain=inventory | tier=errors
package org.example.patterns;

interface InventoryStrategy {
    int apply(int amount);
}

class InventoryNormalStrategy implements InventoryStrategy {
    public int apply(int amount) { return amount; }
}

class InventoryDiscountStrategy implements InventoryStrategy {
    public int apply(int amount) { return amount / 2; }
}

public class InventoryContext {
    private InventoryStrategy strategy;
    public InventoryContext(InventoryStrategy strategy) { this.strategy = strategy; }
    public void setStrategy(InventoryStrategy strategy) { this.strategy = strategy; }
    public int execute(int amount) {
        if (amount < 0) throw new IllegalArgumentException("amount >= 0");
        return strategy.apply(amount);
    }
    public String tag() { return "inventory-strategy"; }
}
