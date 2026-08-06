// DesignPatternsSolid | kind=design_pattern | label=state | domain=http | tier=errors
package org.example.patterns;

interface HttpState {
    String handle(HttpContext ctx);
}

class HttpOnState implements HttpState {
    public String handle(HttpContext ctx) {
        ctx.setState(new HttpOffState());
        return "was-on-http";
    }
}

class HttpOffState implements HttpState {
    public String handle(HttpContext ctx) {
        ctx.setState(new HttpOnState());
        return "was-off-http";
    }
}

public class HttpContext {
    private HttpState state = new HttpOffState();
    public void setState(HttpState state) { this.state = state; }
    public String request() { return state.handle(this); }
}
