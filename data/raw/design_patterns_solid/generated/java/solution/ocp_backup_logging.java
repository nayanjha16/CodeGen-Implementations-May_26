// DesignPatternsSolid | kind=solid | label=ocp | domain=backup | tier=logging
package org.example.patterns;

// OCP: extend via new discount policy without editing engine
interface BackupDiscount {
    int apply(int price);
}

class BackupNoDiscount implements BackupDiscount {
    public int apply(int price) { return price; }
}

class BackupTenPercent implements BackupDiscount {
    public int apply(int price) { return price - price / 10; }
}

public class BackupPriceEngine {
    private final BackupDiscount discount;
    public BackupPriceEngine(BackupDiscount discount) { this.discount = discount; }
    public int quote(int price) { return discount.apply(price); }
    public String domain() { return "backup"; }
}
