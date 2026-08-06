// DesignPatternsSolid | kind=solid | label=ocp | domain=session | tier=logging
package org.example.patterns;

// OCP: extend via new discount policy without editing engine
interface SessionDiscount {
    int apply(int price);
}

class SessionNoDiscount implements SessionDiscount {
    public int apply(int price) { return price; }
}

class SessionTenPercent implements SessionDiscount {
    public int apply(int price) { return price - price / 10; }
}

public class SessionPriceEngine {
    private final SessionDiscount discount;
    public SessionPriceEngine(SessionDiscount discount) { this.discount = discount; }
    public int quote(int price) { return discount.apply(price); }
    public String domain() { return "session"; }
}
