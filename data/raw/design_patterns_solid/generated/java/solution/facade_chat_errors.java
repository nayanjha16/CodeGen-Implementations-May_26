// DesignPatternsSolid | kind=design_pattern | label=facade | domain=chat | tier=errors
package org.example.patterns;

class ChatValidator {
    public boolean ok(String v) { return v != null && !v.isEmpty(); }
}
class ChatWriter {
    public String write(String v) { return "wrote-chat:" + v; }
}
public class ChatFacade {
    private final ChatValidator validator = new ChatValidator();
    private final ChatWriter writer = new ChatWriter();
    public String submit(String value) {
        if (!validator.ok(value)) return "invalid";
        return writer.write(value);
    }
}
