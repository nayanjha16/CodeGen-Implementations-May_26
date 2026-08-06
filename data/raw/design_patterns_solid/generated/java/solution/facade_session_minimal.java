// DesignPatternsSolid | kind=design_pattern | label=facade | domain=session | tier=minimal
package org.example.patterns;

class SessionValidator {
    public boolean ok(String v) { return v != null && !v.isEmpty(); }
}
class SessionWriter {
    public String write(String v) { return "wrote-session:" + v; }
}
public class SessionFacade {
    private final SessionValidator validator = new SessionValidator();
    private final SessionWriter writer = new SessionWriter();
    public String submit(String value) {
        if (!validator.ok(value)) return "invalid";
        return writer.write(value);
    }
}
