// DesignPatternsSolid | kind=design_pattern | label=state | domain=auth | tier=minimal
package org.example.patterns;

interface AuthState {
    String handle(AuthContext ctx);
}

class AuthOnState implements AuthState {
    public String handle(AuthContext ctx) {
        ctx.setState(new AuthOffState());
        return "was-on-auth";
    }
}

class AuthOffState implements AuthState {
    public String handle(AuthContext ctx) {
        ctx.setState(new AuthOnState());
        return "was-off-auth";
    }
}

public class AuthContext {
    private AuthState state = new AuthOffState();
    public void setState(AuthState state) { this.state = state; }
    public String request() { return state.handle(this); }
}
