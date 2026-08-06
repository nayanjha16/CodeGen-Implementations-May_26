// DesignPatternsSolid | kind=design_pattern | label=state | domain=queue | tier=errors
package org.example.patterns;

interface QueueState {
    String handle(QueueContext ctx);
}

class QueueOnState implements QueueState {
    public String handle(QueueContext ctx) {
        ctx.setState(new QueueOffState());
        return "was-on-queue";
    }
}

class QueueOffState implements QueueState {
    public String handle(QueueContext ctx) {
        ctx.setState(new QueueOnState());
        return "was-off-queue";
    }
}

public class QueueContext {
    private QueueState state = new QueueOffState();
    public void setState(QueueState state) { this.state = state; }
    public String request() { return state.handle(this); }
}
