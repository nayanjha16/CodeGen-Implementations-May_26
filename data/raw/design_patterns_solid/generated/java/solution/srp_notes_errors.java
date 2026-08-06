// DesignPatternsSolid | kind=solid | label=srp | domain=notes | tier=errors
package org.example.patterns;

// SRP: separate persistence from formatting for notes
class NotesRecord {
    public final String id;
    public final int amount;
    public NotesRecord(String id, int amount) { this.id = id; this.amount = amount; }
}

class NotesRepository {
    public String save(NotesRecord r) { return "saved-notes:" + r.id; }
}

public class NotesFormatter {
    public String format(NotesRecord r) { return r.id + "=" + r.amount; }
}
