// DesignPatternsSolid | kind=design_pattern | label=decorator | domain=shipping | tier=minimal
package org.example.patterns;

interface ShippingComponent {
    String process(String input);
}

class ShippingCore implements ShippingComponent {
    public String process(String input) { return "shipping:" + input; }
}

public class ShippingUpperDecorator implements ShippingComponent {
    private final ShippingComponent inner;
    public ShippingUpperDecorator(ShippingComponent inner) { this.inner = inner; }
    public String process(String input) {
        return inner.process(input).toUpperCase();
    }
}
