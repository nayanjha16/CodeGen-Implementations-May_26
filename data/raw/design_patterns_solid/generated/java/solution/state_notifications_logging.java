// DesignPatternsSolid | kind=design_pattern | label=state | domain=notifications | tier=logging
package org.example.patterns;

interface NotificationsState {
    String handle(NotificationsContext ctx);
}

class NotificationsOnState implements NotificationsState {
    public String handle(NotificationsContext ctx) {
        ctx.setState(new NotificationsOffState());
        return "was-on-notifications";
    }
}

class NotificationsOffState implements NotificationsState {
    public String handle(NotificationsContext ctx) {
        ctx.setState(new NotificationsOnState());
        return "was-off-notifications";
    }
}

public class NotificationsContext {
    private NotificationsState state = new NotificationsOffState();
    public void setState(NotificationsState state) { this.state = state; }
    public String request() { return state.handle(this); }
}
