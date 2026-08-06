// DesignPatternsSolid | kind=solid | label=srp | domain=feed | tier=logging
package org.example.patterns;

// SRP: separate persistence from formatting for feed
class FeedRecord {
    public final String id;
    public final int amount;
    public FeedRecord(String id, int amount) { this.id = id; this.amount = amount; }
}

class FeedRepository {
    public String save(FeedRecord r) { return "saved-feed:" + r.id; }
}

public class FeedFormatter {
    public String format(FeedRecord r) { return r.id + "=" + r.amount; }
}
