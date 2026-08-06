// DesignPatternsSolid | kind=design_pattern | label=state | domain=tax | tier=errors
package org.example.patterns;

interface TaxState {
    String handle(TaxContext ctx);
}

class TaxOnState implements TaxState {
    public String handle(TaxContext ctx) {
        ctx.setState(new TaxOffState());
        return "was-on-tax";
    }
}

class TaxOffState implements TaxState {
    public String handle(TaxContext ctx) {
        ctx.setState(new TaxOnState());
        return "was-off-tax";
    }
}

public class TaxContext {
    private TaxState state = new TaxOffState();
    public void setState(TaxState state) { this.state = state; }
    public String request() { return state.handle(this); }
}
