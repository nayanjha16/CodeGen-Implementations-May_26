// DesignPatternsSolid | kind=design_pattern | label=facade | domain=tax | tier=logging
package org.example.patterns;

class TaxValidator {
    public boolean ok(String v) { return v != null && !v.isEmpty(); }
}
class TaxWriter {
    public String write(String v) { return "wrote-tax:" + v; }
}
public class TaxFacade {
    private final TaxValidator validator = new TaxValidator();
    private final TaxWriter writer = new TaxWriter();
    public String submit(String value) {
        if (!validator.ok(value)) return "invalid";
        return writer.write(value);
    }
}
