// DesignPatternsSolid | kind=design_pattern | label=facade | domain=report | tier=logging
package org.example.patterns;

class ReportValidator {
    public boolean ok(String v) { return v != null && !v.isEmpty(); }
}
class ReportWriter {
    public String write(String v) { return "wrote-report:" + v; }
}
public class ReportFacade {
    private final ReportValidator validator = new ReportValidator();
    private final ReportWriter writer = new ReportWriter();
    public String submit(String value) {
        if (!validator.ok(value)) return "invalid";
        return writer.write(value);
    }
}
