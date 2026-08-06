// DesignPatternsSolid | kind=design_pattern | label=facade | domain=database | tier=logging
package org.example.patterns;

class DatabaseValidator {
    public boolean ok(String v) { return v != null && !v.isEmpty(); }
}
class DatabaseWriter {
    public String write(String v) { return "wrote-database:" + v; }
}
public class DatabaseFacade {
    private final DatabaseValidator validator = new DatabaseValidator();
    private final DatabaseWriter writer = new DatabaseWriter();
    public String submit(String value) {
        if (!validator.ok(value)) return "invalid";
        return writer.write(value);
    }
}
