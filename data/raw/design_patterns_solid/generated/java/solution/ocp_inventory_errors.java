// DesignPatternsSolid | kind=solid | label=ocp | domain=inventory | tier=errors
package org.example.patterns;

// OCP: extend via new discount policy without editing engine
interface InventoryDiscount {
    int apply(int price);
}

class InventoryNoDiscount implements InventoryDiscount {
    public int apply(int price) { return price; }
}

class InventoryTenPercent implements InventoryDiscount {
    public int apply(int price) { return price - price / 10; }
}

public class InventoryPriceEngine {
    private final InventoryDiscount discount;
    public InventoryPriceEngine(InventoryDiscount discount) { this.discount = discount; }
    public int quote(int price) { return discount.apply(price); }
    public String domain() { return "inventory"; }
}
