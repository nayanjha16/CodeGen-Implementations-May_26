// DesignPatternsSolid | kind=design_pattern | label=facade | domain=analytics | tier=logging
package org.example.patterns;

class AnalyticsValidator {
    public boolean ok(String v) { return v != null && !v.isEmpty(); }
}
class AnalyticsWriter {
    public String write(String v) { return "wrote-analytics:" + v; }
}
public class AnalyticsFacade {
    private final AnalyticsValidator validator = new AnalyticsValidator();
    private final AnalyticsWriter writer = new AnalyticsWriter();
    public String submit(String value) {
        if (!validator.ok(value)) return "invalid";
        return writer.write(value);
    }
}
