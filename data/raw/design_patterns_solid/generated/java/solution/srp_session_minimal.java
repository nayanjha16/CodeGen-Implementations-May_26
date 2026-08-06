// DesignPatternsSolid | kind=solid | label=srp | domain=session | tier=minimal
package org.example.patterns;

// SRP: separate persistence from formatting for session
class SessionRecord {
    public final String id;
    public final int amount;
    public SessionRecord(String id, int amount) { this.id = id; this.amount = amount; }
}

class SessionRepository {
    public String save(SessionRecord r) { return "saved-session:" + r.id; }
}

public class SessionFormatter {
    public String format(SessionRecord r) { return r.id + "=" + r.amount; }
}
