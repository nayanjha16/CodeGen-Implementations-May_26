// DesignPatternsSolid | kind=design_pattern | label=state | domain=scheduling | tier=errors
package org.example.patterns;

interface SchedulingState {
    String handle(SchedulingContext ctx);
}

class SchedulingOnState implements SchedulingState {
    public String handle(SchedulingContext ctx) {
        ctx.setState(new SchedulingOffState());
        return "was-on-scheduling";
    }
}

class SchedulingOffState implements SchedulingState {
    public String handle(SchedulingContext ctx) {
        ctx.setState(new SchedulingOnState());
        return "was-off-scheduling";
    }
}

public class SchedulingContext {
    private SchedulingState state = new SchedulingOffState();
    public void setState(SchedulingState state) { this.state = state; }
    public String request() { return state.handle(this); }
}
