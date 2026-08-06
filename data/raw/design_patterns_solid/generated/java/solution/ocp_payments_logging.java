// DesignPatternsSolid | kind=solid | label=ocp | domain=payments | tier=logging
package org.example.patterns;

// OCP: extend via new discount policy without editing engine
interface PaymentsDiscount {
    int apply(int price);
}

class PaymentsNoDiscount implements PaymentsDiscount {
    public int apply(int price) { return price; }
}

class PaymentsTenPercent implements PaymentsDiscount {
    public int apply(int price) { return price - price / 10; }
}

public class PaymentsPriceEngine {
    private final PaymentsDiscount discount;
    public PaymentsPriceEngine(PaymentsDiscount discount) { this.discount = discount; }
    public int quote(int price) { return discount.apply(price); }
    public String domain() { return "payments"; }
}
