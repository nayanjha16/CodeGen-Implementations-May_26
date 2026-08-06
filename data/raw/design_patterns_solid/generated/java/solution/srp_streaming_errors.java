// DesignPatternsSolid | kind=solid | label=srp | domain=streaming | tier=errors
package org.example.patterns;

// SRP: separate persistence from formatting for streaming
class StreamingRecord {
    public final String id;
    public final int amount;
    public StreamingRecord(String id, int amount) { this.id = id; this.amount = amount; }
}

class StreamingRepository {
    public String save(StreamingRecord r) { return "saved-streaming:" + r.id; }
}

public class StreamingFormatter {
    public String format(StreamingRecord r) { return r.id + "=" + r.amount; }
}
