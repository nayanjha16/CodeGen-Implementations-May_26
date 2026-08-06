// DesignPatternsSolid | kind=design_pattern | label=facade | domain=discount | tier=logging
package org.example.patterns;

class DiscountValidator {
    public boolean ok(String v) { return v != null && !v.isEmpty(); }
}
class DiscountWriter {
    public String write(String v) { return "wrote-discount:" + v; }
}
public class DiscountFacade {
    private final DiscountValidator validator = new DiscountValidator();
    private final DiscountWriter writer = new DiscountWriter();
    public String submit(String value) {
        if (!validator.ok(value)) return "invalid";
        return writer.write(value);
    }
}
