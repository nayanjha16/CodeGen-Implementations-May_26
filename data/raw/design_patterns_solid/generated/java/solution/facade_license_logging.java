// DesignPatternsSolid | kind=design_pattern | label=facade | domain=license | tier=logging
package org.example.patterns;

class LicenseValidator {
    public boolean ok(String v) { return v != null && !v.isEmpty(); }
}
class LicenseWriter {
    public String write(String v) { return "wrote-license:" + v; }
}
public class LicenseFacade {
    private final LicenseValidator validator = new LicenseValidator();
    private final LicenseWriter writer = new LicenseWriter();
    public String submit(String value) {
        if (!validator.ok(value)) return "invalid";
        return writer.write(value);
    }
}
