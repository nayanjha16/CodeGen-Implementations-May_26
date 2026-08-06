// DesignPatternsSolid | kind=solid | label=ocp | domain=queue | tier=minimal
package org.example.patterns;

// OCP: extend via new discount policy without editing engine
interface QueueDiscount {
    int apply(int price);
}

class QueueNoDiscount implements QueueDiscount {
    public int apply(int price) { return price; }
}

class QueueTenPercent implements QueueDiscount {
    public int apply(int price) { return price - price / 10; }
}

public class QueuePriceEngine {
    private final QueueDiscount discount;
    public QueuePriceEngine(QueueDiscount discount) { this.discount = discount; }
    public int quote(int price) { return discount.apply(price); }
    public String domain() { return "queue"; }
}
