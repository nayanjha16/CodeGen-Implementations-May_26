// DesignPatternsSolid | kind=design_pattern | label=state | domain=shipping | tier=logging
package org.example.patterns;

interface ShippingState {
    String handle(ShippingContext ctx);
}

class ShippingOnState implements ShippingState {
    public String handle(ShippingContext ctx) {
        ctx.setState(new ShippingOffState());
        return "was-on-shipping";
    }
}

class ShippingOffState implements ShippingState {
    public String handle(ShippingContext ctx) {
        ctx.setState(new ShippingOnState());
        return "was-off-shipping";
    }
}

public class ShippingContext {
    private ShippingState state = new ShippingOffState();
    public void setState(ShippingState state) { this.state = state; }
    public String request() { return state.handle(this); }
}
