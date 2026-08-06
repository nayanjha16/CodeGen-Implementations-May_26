// DesignPatternsSolid | kind=design_pattern | label=chain of responsibility | domain=scheduling | tier=logging
package org.example.patterns;

public abstract class SchedulingHandler {
    protected SchedulingHandler next;
    public SchedulingHandler link(SchedulingHandler n) { next = n; return n; }
    public String handle(int level, String msg) {
        if (canHandle(level)) return doHandle(msg);
        if (next != null) return next.handle(level, msg);
        return "unhandled-scheduling";
    }
    protected abstract boolean canHandle(int level);
    protected abstract String doHandle(String msg);
}

class SchedulingLowHandler extends SchedulingHandler {
    protected boolean canHandle(int level) { return level <= 1; }
    protected String doHandle(String msg) { return "low-scheduling:" + msg; }
}

class SchedulingHighHandler extends SchedulingHandler {
    protected boolean canHandle(int level) { return level > 1; }
    protected String doHandle(String msg) { return "high-scheduling:" + msg; }
}
