// DesignPatternsSolid | kind=design_pattern | label=facade | domain=notes | tier=minimal
package org.example.patterns;

class NotesValidator {
    public boolean ok(String v) { return v != null && !v.isEmpty(); }
}
class NotesWriter {
    public String write(String v) { return "wrote-notes:" + v; }
}
public class NotesFacade {
    private final NotesValidator validator = new NotesValidator();
    private final NotesWriter writer = new NotesWriter();
    public String submit(String value) {
        if (!validator.ok(value)) return "invalid";
        return writer.write(value);
    }
}
