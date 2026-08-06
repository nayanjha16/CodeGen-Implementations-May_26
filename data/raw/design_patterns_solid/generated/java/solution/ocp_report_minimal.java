// DesignPatternsSolid | kind=solid | label=ocp | domain=report | tier=minimal
package org.example.patterns;

// OCP: extend via new discount policy without editing engine
interface ReportDiscount {
    int apply(int price);
}

class ReportNoDiscount implements ReportDiscount {
    public int apply(int price) { return price; }
}

class ReportTenPercent implements ReportDiscount {
    public int apply(int price) { return price - price / 10; }
}

public class ReportPriceEngine {
    private final ReportDiscount discount;
    public ReportPriceEngine(ReportDiscount discount) { this.discount = discount; }
    public int quote(int price) { return discount.apply(price); }
    public String domain() { return "report"; }
}
