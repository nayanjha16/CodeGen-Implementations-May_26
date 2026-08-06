// DesignPatternsSolid | kind=solid | label=srp | domain=notifications | tier=minimal
package org.example.patterns;

// SRP: separate persistence from formatting for notifications
class NotificationsRecord {
    public final String id;
    public final int amount;
    public NotificationsRecord(String id, int amount) { this.id = id; this.amount = amount; }
}

class NotificationsRepository {
    public String save(NotificationsRecord r) { return "saved-notifications:" + r.id; }
}

public class NotificationsFormatter {
    public String format(NotificationsRecord r) { return r.id + "=" + r.amount; }
}
