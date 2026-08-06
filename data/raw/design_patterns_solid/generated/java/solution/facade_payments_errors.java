// DesignPatternsSolid | kind=design_pattern | label=facade | domain=payments | tier=errors
package org.example.patterns;

class PaymentsValidator {
    public boolean ok(String v) { return v != null && !v.isEmpty(); }
}
class PaymentsWriter {
    public String write(String v) { return "wrote-payments:" + v; }
}
public class PaymentsFacade {
    private final PaymentsValidator validator = new PaymentsValidator();
    private final PaymentsWriter writer = new PaymentsWriter();
    public String submit(String value) {
        if (!validator.ok(value)) return "invalid";
        return writer.write(value);
    }
}
