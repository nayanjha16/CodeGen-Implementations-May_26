// DesignPatternsSolid | kind=design_pattern | label=chain of responsibility | domain=notifications | tier=errors
package org.example.patterns;

public abstract class NotificationsHandler {
    protected NotificationsHandler next;
    public NotificationsHandler link(NotificationsHandler n) { next = n; return n; }
    public String handle(int level, String msg) {
        if (canHandle(level)) return doHandle(msg);
        if (next != null) return next.handle(level, msg);
        return "unhandled-notifications";
    }
    protected abstract boolean canHandle(int level);
    protected abstract String doHandle(String msg);
}

class NotificationsLowHandler extends NotificationsHandler {
    protected boolean canHandle(int level) { return level <= 1; }
    protected String doHandle(String msg) { return "low-notifications:" + msg; }
}

class NotificationsHighHandler extends NotificationsHandler {
    protected boolean canHandle(int level) { return level > 1; }
    protected String doHandle(String msg) { return "high-notifications:" + msg; }
}
