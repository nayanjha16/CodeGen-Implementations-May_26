// DesignPatternsSolid | kind=design_pattern | label=state | domain=metrics | tier=minimal
package org.example.patterns;

interface MetricsState {
    String handle(MetricsContext ctx);
}

class MetricsOnState implements MetricsState {
    public String handle(MetricsContext ctx) {
        ctx.setState(new MetricsOffState());
        return "was-on-metrics";
    }
}

class MetricsOffState implements MetricsState {
    public String handle(MetricsContext ctx) {
        ctx.setState(new MetricsOnState());
        return "was-off-metrics";
    }
}

public class MetricsContext {
    private MetricsState state = new MetricsOffState();
    public void setState(MetricsState state) { this.state = state; }
    public String request() { return state.handle(this); }
}
