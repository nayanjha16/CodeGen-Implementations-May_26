// DesignPatternsSolid | kind=design_pattern | label=facade | domain=metrics | tier=minimal
package org.example.patterns;

class MetricsValidator {
    public boolean ok(String v) { return v != null && !v.isEmpty(); }
}
class MetricsWriter {
    public String write(String v) { return "wrote-metrics:" + v; }
}
public class MetricsFacade {
    private final MetricsValidator validator = new MetricsValidator();
    private final MetricsWriter writer = new MetricsWriter();
    public String submit(String value) {
        if (!validator.ok(value)) return "invalid";
        return writer.write(value);
    }
}
