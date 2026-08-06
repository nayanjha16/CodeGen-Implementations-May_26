// DesignPatternsSolid | kind=design_pattern | label=facade | domain=billing | tier=logging
package org.example.patterns;

class BillingValidator {
    public boolean ok(String v) { return v != null && !v.isEmpty(); }
}
class BillingWriter {
    public String write(String v) { return "wrote-billing:" + v; }
}
public class BillingFacade {
    private final BillingValidator validator = new BillingValidator();
    private final BillingWriter writer = new BillingWriter();
    public String submit(String value) {
        if (!validator.ok(value)) return "invalid";
        return writer.write(value);
    }
}
