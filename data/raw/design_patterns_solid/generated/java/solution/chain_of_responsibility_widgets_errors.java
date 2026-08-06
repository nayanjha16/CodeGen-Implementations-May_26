// DesignPatternsSolid | kind=design_pattern | label=chain of responsibility | domain=widgets | tier=errors
package org.example.patterns;

public abstract class WidgetsHandler {
    protected WidgetsHandler next;
    public WidgetsHandler link(WidgetsHandler n) { next = n; return n; }
    public String handle(int level, String msg) {
        if (canHandle(level)) return doHandle(msg);
        if (next != null) return next.handle(level, msg);
        return "unhandled-widgets";
    }
    protected abstract boolean canHandle(int level);
    protected abstract String doHandle(String msg);
}

class WidgetsLowHandler extends WidgetsHandler {
    protected boolean canHandle(int level) { return level <= 1; }
    protected String doHandle(String msg) { return "low-widgets:" + msg; }
}

class WidgetsHighHandler extends WidgetsHandler {
    protected boolean canHandle(int level) { return level > 1; }
    protected String doHandle(String msg) { return "high-widgets:" + msg; }
}
