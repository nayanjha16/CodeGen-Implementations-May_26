// DesignPatternsSolid | kind=design_pattern | label=facade | domain=sms | tier=minimal
package org.example.patterns;

class SmsValidator {
    public boolean ok(String v) { return v != null && !v.isEmpty(); }
}
class SmsWriter {
    public String write(String v) { return "wrote-sms:" + v; }
}
public class SmsFacade {
    private final SmsValidator validator = new SmsValidator();
    private final SmsWriter writer = new SmsWriter();
    public String submit(String value) {
        if (!validator.ok(value)) return "invalid";
        return writer.write(value);
    }
}
