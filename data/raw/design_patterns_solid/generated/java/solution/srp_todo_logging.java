// DesignPatternsSolid | kind=solid | label=srp | domain=todo | tier=logging
package org.example.patterns;

// SRP: separate persistence from formatting for todo
class TodoRecord {
    public final String id;
    public final int amount;
    public TodoRecord(String id, int amount) { this.id = id; this.amount = amount; }
}

class TodoRepository {
    public String save(TodoRecord r) { return "saved-todo:" + r.id; }
}

public class TodoFormatter {
    public String format(TodoRecord r) { return r.id + "=" + r.amount; }
}
