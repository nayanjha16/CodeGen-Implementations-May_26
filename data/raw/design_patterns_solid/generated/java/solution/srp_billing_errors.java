// DesignPatternsSolid | kind=solid | label=srp | domain=billing | tier=errors
package org.example.patterns;

// SRP: separate persistence from formatting for billing
class BillingRecord {
    public final String id;
    public final int amount;
    public BillingRecord(String id, int amount) { this.id = id; this.amount = amount; }
}

class BillingRepository {
    public String save(BillingRecord r) { return "saved-billing:" + r.id; }
}

public class BillingFormatter {
    public String format(BillingRecord r) { return r.id + "=" + r.amount; }
}
