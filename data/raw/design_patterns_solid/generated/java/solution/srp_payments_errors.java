// DesignPatternsSolid | kind=solid | label=srp | domain=payments | tier=errors
package org.example.patterns;

// SRP: separate persistence from formatting for payments
class PaymentsRecord {
    public final String id;
    public final int amount;
    public PaymentsRecord(String id, int amount) { this.id = id; this.amount = amount; }
}

class PaymentsRepository {
    public String save(PaymentsRecord r) { return "saved-payments:" + r.id; }
}

public class PaymentsFormatter {
    public String format(PaymentsRecord r) { return r.id + "=" + r.amount; }
}
