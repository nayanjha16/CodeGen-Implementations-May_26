// DesignPatternsSolid | kind=solid | label=srp | domain=editor | tier=errors
package org.example.patterns;

// SRP: separate persistence from formatting for editor
class EditorRecord {
    public final String id;
    public final int amount;
    public EditorRecord(String id, int amount) { this.id = id; this.amount = amount; }
}

class EditorRepository {
    public String save(EditorRecord r) { return "saved-editor:" + r.id; }
}

public class EditorFormatter {
    public String format(EditorRecord r) { return r.id + "=" + r.amount; }
}
