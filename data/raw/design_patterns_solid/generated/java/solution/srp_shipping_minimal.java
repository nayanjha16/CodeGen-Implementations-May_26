// DesignPatternsSolid | kind=solid | label=srp | domain=shipping | tier=minimal
package org.example.patterns;

// SRP: separate persistence from formatting for shipping
class ShippingRecord {
    public final String id;
    public final int amount;
    public ShippingRecord(String id, int amount) { this.id = id; this.amount = amount; }
}

class ShippingRepository {
    public String save(ShippingRecord r) { return "saved-shipping:" + r.id; }
}

public class ShippingFormatter {
    public String format(ShippingRecord r) { return r.id + "=" + r.amount; }
}
