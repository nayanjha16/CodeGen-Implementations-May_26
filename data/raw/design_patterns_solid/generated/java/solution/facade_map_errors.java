// DesignPatternsSolid | kind=design_pattern | label=facade | domain=map | tier=errors
package org.example.patterns;

class MapValidator {
    public boolean ok(String v) { return v != null && !v.isEmpty(); }
}
class MapWriter {
    public String write(String v) { return "wrote-map:" + v; }
}
public class MapFacade {
    private final MapValidator validator = new MapValidator();
    private final MapWriter writer = new MapWriter();
    public String submit(String value) {
        if (!validator.ok(value)) return "invalid";
        return writer.write(value);
    }
}
