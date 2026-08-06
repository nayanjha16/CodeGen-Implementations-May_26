// DesignPatternsSolid | kind=design_pattern | label=facade | domain=feed | tier=logging
package org.example.patterns;

class FeedValidator {
    public boolean ok(String v) { return v != null && !v.isEmpty(); }
}
class FeedWriter {
    public String write(String v) { return "wrote-feed:" + v; }
}
public class FeedFacade {
    private final FeedValidator validator = new FeedValidator();
    private final FeedWriter writer = new FeedWriter();
    public String submit(String value) {
        if (!validator.ok(value)) return "invalid";
        return writer.write(value);
    }
}
