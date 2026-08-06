// DesignPatternsSolid | kind=design_pattern | label=facade | domain=editor | tier=logging
package org.example.patterns;

class EditorValidator {
    public boolean ok(String v) { return v != null && !v.isEmpty(); }
}
class EditorWriter {
    public String write(String v) { return "wrote-editor:" + v; }
}
public class EditorFacade {
    private final EditorValidator validator = new EditorValidator();
    private final EditorWriter writer = new EditorWriter();
    public String submit(String value) {
        if (!validator.ok(value)) return "invalid";
        return writer.write(value);
    }
}
