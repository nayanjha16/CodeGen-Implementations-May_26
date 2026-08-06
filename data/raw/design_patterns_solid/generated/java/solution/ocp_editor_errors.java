// DesignPatternsSolid | kind=solid | label=ocp | domain=editor | tier=errors
package org.example.patterns;

// OCP: extend via new discount policy without editing engine
interface EditorDiscount {
    int apply(int price);
}

class EditorNoDiscount implements EditorDiscount {
    public int apply(int price) { return price; }
}

class EditorTenPercent implements EditorDiscount {
    public int apply(int price) { return price - price / 10; }
}

public class EditorPriceEngine {
    private final EditorDiscount discount;
    public EditorPriceEngine(EditorDiscount discount) { this.discount = discount; }
    public int quote(int price) { return discount.apply(price); }
    public String domain() { return "editor"; }
}
