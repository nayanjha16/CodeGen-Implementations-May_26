// DesignPatternsSolid | kind=design_pattern | label=facade | domain=config | tier=logging
package org.example.patterns;

class ConfigValidator {
    public boolean ok(String v) { return v != null && !v.isEmpty(); }
}
class ConfigWriter {
    public String write(String v) { return "wrote-config:" + v; }
}
public class ConfigFacade {
    private final ConfigValidator validator = new ConfigValidator();
    private final ConfigWriter writer = new ConfigWriter();
    public String submit(String value) {
        if (!validator.ok(value)) return "invalid";
        return writer.write(value);
    }
}
