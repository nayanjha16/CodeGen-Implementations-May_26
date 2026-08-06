// DesignPatternsSolid | kind=design_pattern | label=state | domain=logging | tier=minimal
package org.example.patterns;

interface LoggingState {
    String handle(LoggingContext ctx);
}

class LoggingOnState implements LoggingState {
    public String handle(LoggingContext ctx) {
        ctx.setState(new LoggingOffState());
        return "was-on-logging";
    }
}

class LoggingOffState implements LoggingState {
    public String handle(LoggingContext ctx) {
        ctx.setState(new LoggingOnState());
        return "was-off-logging";
    }
}

public class LoggingContext {
    private LoggingState state = new LoggingOffState();
    public void setState(LoggingState state) { this.state = state; }
    public String request() { return state.handle(this); }
}
