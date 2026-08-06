// DesignPatternsSolid | kind=design_pattern | label=state | domain=payments | tier=minimal
package org.example.patterns;

interface PaymentsState {
    String handle(PaymentsContext ctx);
}

class PaymentsOnState implements PaymentsState {
    public String handle(PaymentsContext ctx) {
        ctx.setState(new PaymentsOffState());
        return "was-on-payments";
    }
}

class PaymentsOffState implements PaymentsState {
    public String handle(PaymentsContext ctx) {
        ctx.setState(new PaymentsOnState());
        return "was-off-payments";
    }
}

public class PaymentsContext {
    private PaymentsState state = new PaymentsOffState();
    public void setState(PaymentsState state) { this.state = state; }
    public String request() { return state.handle(this); }
}
