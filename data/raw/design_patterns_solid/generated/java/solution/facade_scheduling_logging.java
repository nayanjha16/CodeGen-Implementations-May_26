// DesignPatternsSolid | kind=design_pattern | label=facade | domain=scheduling | tier=logging
package org.example.patterns;

class SchedulingValidator {
    public boolean ok(String v) { return v != null && !v.isEmpty(); }
}
class SchedulingWriter {
    public String write(String v) { return "wrote-scheduling:" + v; }
}
public class SchedulingFacade {
    private final SchedulingValidator validator = new SchedulingValidator();
    private final SchedulingWriter writer = new SchedulingWriter();
    public String submit(String value) {
        if (!validator.ok(value)) return "invalid";
        return writer.write(value);
    }
}
