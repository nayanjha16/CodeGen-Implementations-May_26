// DesignPatternsSolid | kind=design_pattern | label=facade | domain=plugin | tier=minimal
package org.example.patterns;

class PluginValidator {
    public boolean ok(String v) { return v != null && !v.isEmpty(); }
}
class PluginWriter {
    public String write(String v) { return "wrote-plugin:" + v; }
}
public class PluginFacade {
    private final PluginValidator validator = new PluginValidator();
    private final PluginWriter writer = new PluginWriter();
    public String submit(String value) {
        if (!validator.ok(value)) return "invalid";
        return writer.write(value);
    }
}
