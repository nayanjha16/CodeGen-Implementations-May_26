// DesignPatternsSolid | kind=design_pattern | label=proxy | domain=notes | tier=errors
package org.example.patterns;

interface NotesService {
    String load(String id);
}

class NotesRealService implements NotesService {
    public String load(String id) { return "real-notes:" + id; }
}

public class NotesProxy implements NotesService {
    private NotesRealService real;
    private final boolean allowed;
    public NotesProxy(boolean allowed) { this.allowed = allowed; }
    public String load(String id) {
        if (!allowed) return "denied";
        if (real == null) real = new NotesRealService();
        return real.load(id);
    }
}
