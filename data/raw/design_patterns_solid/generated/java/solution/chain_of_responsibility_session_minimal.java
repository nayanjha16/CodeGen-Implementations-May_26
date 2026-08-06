// DesignPatternsSolid | kind=design_pattern | label=chain of responsibility | domain=session | tier=minimal
package org.example.patterns;

public abstract class SessionHandler {
    protected SessionHandler next;
    public SessionHandler link(SessionHandler n) { next = n; return n; }
    public String handle(int level, String msg) {
        if (canHandle(level)) return doHandle(msg);
        if (next != null) return next.handle(level, msg);
        return "unhandled-session";
    }
    protected abstract boolean canHandle(int level);
    protected abstract String doHandle(String msg);
}

class SessionLowHandler extends SessionHandler {
    protected boolean canHandle(int level) { return level <= 1; }
    protected String doHandle(String msg) { return "low-session:" + msg; }
}

class SessionHighHandler extends SessionHandler {
    protected boolean canHandle(int level) { return level > 1; }
    protected String doHandle(String msg) { return "high-session:" + msg; }
}
