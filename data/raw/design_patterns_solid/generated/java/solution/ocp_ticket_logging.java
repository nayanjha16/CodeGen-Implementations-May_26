// DesignPatternsSolid | kind=solid | label=ocp | domain=ticket | tier=logging
package org.example.patterns;

// OCP: extend via new discount policy without editing engine
interface TicketDiscount {
    int apply(int price);
}

class TicketNoDiscount implements TicketDiscount {
    public int apply(int price) { return price; }
}

class TicketTenPercent implements TicketDiscount {
    public int apply(int price) { return price - price / 10; }
}

public class TicketPriceEngine {
    private final TicketDiscount discount;
    public TicketPriceEngine(TicketDiscount discount) { this.discount = discount; }
    public int quote(int price) { return discount.apply(price); }
    public String domain() { return "ticket"; }
}
