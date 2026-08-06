// DesignPatternsSolid | kind=design_pattern | label=facade | domain=cart | tier=errors
package org.example.patterns;

class CartValidator {
    public boolean ok(String v) { return v != null && !v.isEmpty(); }
}
class CartWriter {
    public String write(String v) { return "wrote-cart:" + v; }
}
public class CartFacade {
    private final CartValidator validator = new CartValidator();
    private final CartWriter writer = new CartWriter();
    public String submit(String value) {
        if (!validator.ok(value)) return "invalid";
        return writer.write(value);
    }
}
