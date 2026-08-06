// DesignPatternsSolid | kind=solid | label=srp | domain=logging | tier=errors
package org.example.patterns;

// SRP: separate persistence from formatting for logging
class LoggingRecord {
    public final String id;
    public final int amount;
    public LoggingRecord(String id, int amount) { this.id = id; this.amount = amount; }
}

class LoggingRepository {
    public String save(LoggingRecord r) { return "saved-logging:" + r.id; }
}

public class LoggingFormatter {
    public String format(LoggingRecord r) { return r.id + "=" + r.amount; }
}
