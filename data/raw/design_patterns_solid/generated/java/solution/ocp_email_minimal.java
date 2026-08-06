// DesignPatternsSolid | kind=solid | label=ocp | domain=email | tier=minimal
package org.example.patterns;

// OCP: extend via new discount policy without editing engine
interface EmailDiscount {
    int apply(int price);
}

class EmailNoDiscount implements EmailDiscount {
    public int apply(int price) { return price; }
}

class EmailTenPercent implements EmailDiscount {
    public int apply(int price) { return price - price / 10; }
}

public class EmailPriceEngine {
    private final EmailDiscount discount;
    public EmailPriceEngine(EmailDiscount discount) { this.discount = discount; }
    public int quote(int price) { return discount.apply(price); }
    public String domain() { return "email"; }
}
