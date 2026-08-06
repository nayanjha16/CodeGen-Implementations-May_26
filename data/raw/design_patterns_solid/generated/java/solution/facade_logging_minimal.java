// DesignPatternsSolid | kind=design_pattern | label=facade | domain=logging | tier=minimal
package org.example.patterns;

class LoggingValidator {
    public boolean ok(String v) { return v != null && !v.isEmpty(); }
}
class LoggingWriter {
    public String write(String v) { return "wrote-logging:" + v; }
}
public class LoggingFacade {
    private final LoggingValidator validator = new LoggingValidator();
    private final LoggingWriter writer = new LoggingWriter();
    public String submit(String value) {
        if (!validator.ok(value)) return "invalid";
        return writer.write(value);
    }
}
