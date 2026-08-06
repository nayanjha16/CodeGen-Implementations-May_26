// DesignPatternsSolid | kind=design_pattern | label=facade | domain=streaming | tier=errors
package org.example.patterns;

class StreamingValidator {
    public boolean ok(String v) { return v != null && !v.isEmpty(); }
}
class StreamingWriter {
    public String write(String v) { return "wrote-streaming:" + v; }
}
public class StreamingFacade {
    private final StreamingValidator validator = new StreamingValidator();
    private final StreamingWriter writer = new StreamingWriter();
    public String submit(String value) {
        if (!validator.ok(value)) return "invalid";
        return writer.write(value);
    }
}
