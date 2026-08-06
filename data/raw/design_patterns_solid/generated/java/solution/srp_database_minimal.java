// DesignPatternsSolid | kind=solid | label=srp | domain=database | tier=minimal
package org.example.patterns;

// SRP: separate persistence from formatting for database
class DatabaseRecord {
    public final String id;
    public final int amount;
    public DatabaseRecord(String id, int amount) { this.id = id; this.amount = amount; }
}

class DatabaseRepository {
    public String save(DatabaseRecord r) { return "saved-database:" + r.id; }
}

public class DatabaseFormatter {
    public String format(DatabaseRecord r) { return r.id + "=" + r.amount; }
}
