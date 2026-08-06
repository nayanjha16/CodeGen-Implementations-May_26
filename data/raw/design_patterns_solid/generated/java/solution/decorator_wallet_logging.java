// DesignPatternsSolid | kind=design_pattern | label=decorator | domain=wallet | tier=logging
package org.example.patterns;

interface WalletComponent {
    String process(String input);
}

class WalletCore implements WalletComponent {
    public String process(String input) { return "wallet:" + input; }
}

public class WalletUpperDecorator implements WalletComponent {
    private final WalletComponent inner;
    public WalletUpperDecorator(WalletComponent inner) { this.inner = inner; }
    public String process(String input) {
        return inner.process(input).toUpperCase();
    }
}
