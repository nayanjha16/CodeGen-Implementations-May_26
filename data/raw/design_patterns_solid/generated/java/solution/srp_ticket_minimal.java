// DesignPatternsSolid | kind=solid | label=srp | domain=ticket | tier=minimal
package org.example.patterns;

// SRP: separate persistence from formatting for ticket
class TicketRecord {
    public final String id;
    public final int amount;
    public TicketRecord(String id, int amount) { this.id = id; this.amount = amount; }
}

class TicketRepository {
    public String save(TicketRecord r) { return "saved-ticket:" + r.id; }
}

public class TicketFormatter {
    public String format(TicketRecord r) { return r.id + "=" + r.amount; }
}
