// DesignPatternsSolid | kind=design_pattern | label=state | domain=report | tier=errors
package org.example.patterns;

interface ReportState {
    String handle(ReportContext ctx);
}

class ReportOnState implements ReportState {
    public String handle(ReportContext ctx) {
        ctx.setState(new ReportOffState());
        return "was-on-report";
    }
}

class ReportOffState implements ReportState {
    public String handle(ReportContext ctx) {
        ctx.setState(new ReportOnState());
        return "was-off-report";
    }
}

public class ReportContext {
    private ReportState state = new ReportOffState();
    public void setState(ReportState state) { this.state = state; }
    public String request() { return state.handle(this); }
}
