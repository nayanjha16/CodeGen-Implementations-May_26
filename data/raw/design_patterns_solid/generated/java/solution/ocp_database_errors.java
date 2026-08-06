// DesignPatternsSolid | kind=solid | label=ocp | domain=database | tier=errors
package org.example.patterns;

// OCP: extend via new discount policy without editing engine
interface DatabaseDiscount {
    int apply(int price);
}

class DatabaseNoDiscount implements DatabaseDiscount {
    public int apply(int price) { return price; }
}

class DatabaseTenPercent implements DatabaseDiscount {
    public int apply(int price) { return price - price / 10; }
}

public class DatabasePriceEngine {
    private final DatabaseDiscount discount;
    public DatabasePriceEngine(DatabaseDiscount discount) { this.discount = discount; }
    public int quote(int price) { return discount.apply(price); }
    public String domain() { return "database"; }
}
