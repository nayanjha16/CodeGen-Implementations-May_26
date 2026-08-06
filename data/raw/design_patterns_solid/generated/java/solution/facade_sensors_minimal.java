// DesignPatternsSolid | kind=design_pattern | label=facade | domain=sensors | tier=minimal
package org.example.patterns;

class SensorsValidator {
    public boolean ok(String v) { return v != null && !v.isEmpty(); }
}
class SensorsWriter {
    public String write(String v) { return "wrote-sensors:" + v; }
}
public class SensorsFacade {
    private final SensorsValidator validator = new SensorsValidator();
    private final SensorsWriter writer = new SensorsWriter();
    public String submit(String value) {
        if (!validator.ok(value)) return "invalid";
        return writer.write(value);
    }
}
