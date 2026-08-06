// DesignPatternsSolid | kind=design_pattern | label=facade | domain=game | tier=minimal
package org.example.patterns;

class GameValidator {
    public boolean ok(String v) { return v != null && !v.isEmpty(); }
}
class GameWriter {
    public String write(String v) { return "wrote-game:" + v; }
}
public class GameFacade {
    private final GameValidator validator = new GameValidator();
    private final GameWriter writer = new GameWriter();
    public String submit(String value) {
        if (!validator.ok(value)) return "invalid";
        return writer.write(value);
    }
}
