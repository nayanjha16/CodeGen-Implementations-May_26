// DesignPatternsSolid | kind=design_pattern | label=facade | domain=cache | tier=logging
package org.example.patterns;

class CacheValidator {
    public boolean ok(String v) { return v != null && !v.isEmpty(); }
}
class CacheWriter {
    public String write(String v) { return "wrote-cache:" + v; }
}
public class CacheFacade {
    private final CacheValidator validator = new CacheValidator();
    private final CacheWriter writer = new CacheWriter();
    public String submit(String value) {
        if (!validator.ok(value)) return "invalid";
        return writer.write(value);
    }
}
