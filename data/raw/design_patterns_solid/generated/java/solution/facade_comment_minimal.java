// DesignPatternsSolid | kind=design_pattern | label=facade | domain=comment | tier=minimal
package org.example.patterns;

class CommentValidator {
    public boolean ok(String v) { return v != null && !v.isEmpty(); }
}
class CommentWriter {
    public String write(String v) { return "wrote-comment:" + v; }
}
public class CommentFacade {
    private final CommentValidator validator = new CommentValidator();
    private final CommentWriter writer = new CommentWriter();
    public String submit(String value) {
        if (!validator.ok(value)) return "invalid";
        return writer.write(value);
    }
}
