// DesignPatternsSolid | kind=design_pattern | label=state | domain=billing | tier=errors
package org.example.patterns;

interface BillingState {
    String handle(BillingContext ctx);
}

class BillingOnState implements BillingState {
    public String handle(BillingContext ctx) {
        ctx.setState(new BillingOffState());
        return "was-on-billing";
    }
}

class BillingOffState implements BillingState {
    public String handle(BillingContext ctx) {
        ctx.setState(new BillingOnState());
        return "was-off-billing";
    }
}

public class BillingContext {
    private BillingState state = new BillingOffState();
    public void setState(BillingState state) { this.state = state; }
    public String request() { return state.handle(this); }
}
