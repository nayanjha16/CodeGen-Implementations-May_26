// DesignPatternsSolid | kind=solid | label=ocp | domain=game | tier=minimal
package org.example.patterns;

// OCP: extend via new discount policy without editing engine
interface GameDiscount {
    int apply(int price);
}

class GameNoDiscount implements GameDiscount {
    public int apply(int price) { return price; }
}

class GameTenPercent implements GameDiscount {
    public int apply(int price) { return price - price / 10; }
}

public class GamePriceEngine {
    private final GameDiscount discount;
    public GamePriceEngine(GameDiscount discount) { this.discount = discount; }
    public int quote(int price) { return discount.apply(price); }
    public String domain() { return "game"; }
}
