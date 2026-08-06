// DesignPatternsSolid | kind=solid | label=ocp | domain=canvas | tier=minimal
package org.example.patterns;

// OCP: extend via new discount policy without editing engine
interface CanvasDiscount {
    int apply(int price);
}

class CanvasNoDiscount implements CanvasDiscount {
    public int apply(int price) { return price; }
}

class CanvasTenPercent implements CanvasDiscount {
    public int apply(int price) { return price - price / 10; }
}

public class CanvasPriceEngine {
    private final CanvasDiscount discount;
    public CanvasPriceEngine(CanvasDiscount discount) { this.discount = discount; }
    public int quote(int price) { return discount.apply(price); }
    public String domain() { return "canvas"; }
}
