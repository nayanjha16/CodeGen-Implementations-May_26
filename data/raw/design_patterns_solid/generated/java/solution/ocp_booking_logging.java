// DesignPatternsSolid | kind=solid | label=ocp | domain=booking | tier=logging
package org.example.patterns;

// OCP: extend via new discount policy without editing engine
interface BookingDiscount {
    int apply(int price);
}

class BookingNoDiscount implements BookingDiscount {
    public int apply(int price) { return price; }
}

class BookingTenPercent implements BookingDiscount {
    public int apply(int price) { return price - price / 10; }
}

public class BookingPriceEngine {
    private final BookingDiscount discount;
    public BookingPriceEngine(BookingDiscount discount) { this.discount = discount; }
    public int quote(int price) { return discount.apply(price); }
    public String domain() { return "booking"; }
}
