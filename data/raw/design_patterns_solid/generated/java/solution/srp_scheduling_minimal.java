// DesignPatternsSolid | kind=solid | label=srp | domain=scheduling | tier=minimal
package org.example.patterns;

// SRP: separate persistence from formatting for scheduling
class SchedulingRecord {
    public final String id;
    public final int amount;
    public SchedulingRecord(String id, int amount) { this.id = id; this.amount = amount; }
}

class SchedulingRepository {
    public String save(SchedulingRecord r) { return "saved-scheduling:" + r.id; }
}

public class SchedulingFormatter {
    public String format(SchedulingRecord r) { return r.id + "=" + r.amount; }
}
