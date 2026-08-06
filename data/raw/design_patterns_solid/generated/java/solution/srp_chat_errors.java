// DesignPatternsSolid | kind=solid | label=srp | domain=chat | tier=errors
package org.example.patterns;

// SRP: separate persistence from formatting for chat
class ChatRecord {
    public final String id;
    public final int amount;
    public ChatRecord(String id, int amount) { this.id = id; this.amount = amount; }
}

class ChatRepository {
    public String save(ChatRecord r) { return "saved-chat:" + r.id; }
}

public class ChatFormatter {
    public String format(ChatRecord r) { return r.id + "=" + r.amount; }
}
