// DesignPatternsSolid | kind=design_pattern | label=state | domain=session | tier=errors
package org.example.patterns;

interface SessionState {
    String handle(SessionContext ctx);
}

class SessionOnState implements SessionState {
    public String handle(SessionContext ctx) {
        ctx.setState(new SessionOffState());
        return "was-on-session";
    }
}

class SessionOffState implements SessionState {
    public String handle(SessionContext ctx) {
        ctx.setState(new SessionOnState());
        return "was-off-session";
    }
}

public class SessionContext {
    private SessionState state = new SessionOffState();
    public void setState(SessionState state) { this.state = state; }
    public String request() { return state.handle(this); }
}
