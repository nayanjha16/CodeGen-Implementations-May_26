// DesignPatternsSolid | kind=design_pattern | label=facade | domain=audio | tier=errors
package org.example.patterns;

class AudioValidator {
    public boolean ok(String v) { return v != null && !v.isEmpty(); }
}
class AudioWriter {
    public String write(String v) { return "wrote-audio:" + v; }
}
public class AudioFacade {
    private final AudioValidator validator = new AudioValidator();
    private final AudioWriter writer = new AudioWriter();
    public String submit(String value) {
        if (!validator.ok(value)) return "invalid";
        return writer.write(value);
    }
}
