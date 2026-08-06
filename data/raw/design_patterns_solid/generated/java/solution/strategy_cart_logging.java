// DesignPatternsSolid | kind=design_pattern | label=strategy | domain=cart | tier=logging
package org.example.patterns;

interface CartStrategy {
    int apply(int amount);
}

class CartNormalStrategy implements CartStrategy {
    public int apply(int amount) { return amount; }
}

class CartDiscountStrategy implements CartStrategy {
    public int apply(int amount) { return amount / 2; }
}

public class CartContext {
    private CartStrategy strategy;
    public CartContext(CartStrategy strategy) { this.strategy = strategy; }
    public void setStrategy(CartStrategy strategy) { this.strategy = strategy; }
    public int execute(int amount) {
        return strategy.apply(amount);
    }
    public String tag() { return "cart-strategy"; }
}
