// DesignPatternsSolid | kind=design_pattern | label=state | domain=sync | tier=minimal
package org.example.patterns;

interface SyncState {
    String handle(SyncContext ctx);
}

class SyncOnState implements SyncState {
    public String handle(SyncContext ctx) {
        ctx.setState(new SyncOffState());
        return "was-on-sync";
    }
}

class SyncOffState implements SyncState {
    public String handle(SyncContext ctx) {
        ctx.setState(new SyncOnState());
        return "was-off-sync";
    }
}

public class SyncContext {
    private SyncState state = new SyncOffState();
    public void setState(SyncState state) { this.state = state; }
    public String request() { return state.handle(this); }
}
