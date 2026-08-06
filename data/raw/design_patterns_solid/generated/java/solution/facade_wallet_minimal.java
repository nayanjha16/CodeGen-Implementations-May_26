// DesignPatternsSolid | kind=design_pattern | label=facade | domain=wallet | tier=minimal
package org.example.patterns;

class WalletValidator {
    public boolean ok(String v) { return v != null && !v.isEmpty(); }
}
class WalletWriter {
    public String write(String v) { return "wrote-wallet:" + v; }
}
public class WalletFacade {
    private final WalletValidator validator = new WalletValidator();
    private final WalletWriter writer = new WalletWriter();
    public String submit(String value) {
        if (!validator.ok(value)) return "invalid";
        return writer.write(value);
    }
}
