// DesignPatternsSolid | kind=design_pattern | label=chain of responsibility | domain=logging | tier=minimal
package org.example.patterns;

public abstract class LoggingHandler {
    protected LoggingHandler next;
    public LoggingHandler link(LoggingHandler n) { next = n; return n; }
    public String handle(int level, String msg) {
        if (canHandle(level)) return doHandle(msg);
        if (next != null) return next.handle(level, msg);
        return "unhandled-logging";
    }
    protected abstract boolean canHandle(int level);
    protected abstract String doHandle(String msg);
}

class LoggingLowHandler extends LoggingHandler {
    protected boolean canHandle(int level) { return level <= 1; }
    protected String doHandle(String msg) { return "low-logging:" + msg; }
}

class LoggingHighHandler extends LoggingHandler {
    protected boolean canHandle(int level) { return level > 1; }
    protected String doHandle(String msg) { return "high-logging:" + msg; }
}
