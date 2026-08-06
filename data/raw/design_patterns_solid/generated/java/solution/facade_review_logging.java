// DesignPatternsSolid | kind=design_pattern | label=facade | domain=review | tier=logging
package org.example.patterns;

class ReviewValidator {
    public boolean ok(String v) { return v != null && !v.isEmpty(); }
}
class ReviewWriter {
    public String write(String v) { return "wrote-review:" + v; }
}
public class ReviewFacade {
    private final ReviewValidator validator = new ReviewValidator();
    private final ReviewWriter writer = new ReviewWriter();
    public String submit(String value) {
        if (!validator.ok(value)) return "invalid";
        return writer.write(value);
    }
}
