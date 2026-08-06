// DesignPatternsSolid | kind=combo | label=strategy+ocp | domain=shipping | tier=minimal
package org.example.patterns;

interface ShippingStrategy {
    int apply(int amount);
}

class ShippingNormalStrategy implements ShippingStrategy {
    public int apply(int amount) { return amount; }
}

class ShippingDiscountStrategy implements ShippingStrategy {
    public int apply(int amount) { return amount / 2; }
}

public class ShippingContext {
    private ShippingStrategy strategy;
    public ShippingContext(ShippingStrategy strategy) { this.strategy = strategy; }
    public void setStrategy(ShippingStrategy strategy) { this.strategy = strategy; }
    public int execute(int amount) {
        return strategy.apply(amount);
    }
    public String tag() { return "shipping-strategy"; }
}
