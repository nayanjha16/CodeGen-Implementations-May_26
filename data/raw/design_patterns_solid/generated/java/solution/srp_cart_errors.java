// DesignPatternsSolid | kind=solid | label=srp | domain=cart | tier=errors
package org.example.patterns;

// SRP: separate persistence from formatting for cart
class CartRecord {
    public final String id;
    public final int amount;
    public CartRecord(String id, int amount) { this.id = id; this.amount = amount; }
}

class CartRepository {
    public String save(CartRecord r) { return "saved-cart:" + r.id; }
}

public class CartFormatter {
    public String format(CartRecord r) { return r.id + "=" + r.amount; }
}
