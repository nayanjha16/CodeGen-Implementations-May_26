// DesignPatternsSolid | kind=design_pattern | label=state | domain=email | tier=errors
package org.example.patterns;

interface EmailState {
    String handle(EmailContext ctx);
}

class EmailOnState implements EmailState {
    public String handle(EmailContext ctx) {
        ctx.setState(new EmailOffState());
        return "was-on-email";
    }
}

class EmailOffState implements EmailState {
    public String handle(EmailContext ctx) {
        ctx.setState(new EmailOnState());
        return "was-off-email";
    }
}

public class EmailContext {
    private EmailState state = new EmailOffState();
    public void setState(EmailState state) { this.state = state; }
    public String request() { return state.handle(this); }
}
