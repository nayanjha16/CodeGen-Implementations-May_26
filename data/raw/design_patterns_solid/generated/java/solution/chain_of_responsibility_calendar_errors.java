// DesignPatternsSolid | kind=design_pattern | label=chain of responsibility | domain=calendar | tier=errors
package org.example.patterns;

public abstract class CalendarHandler {
    protected CalendarHandler next;
    public CalendarHandler link(CalendarHandler n) { next = n; return n; }
    public String handle(int level, String msg) {
        if (canHandle(level)) return doHandle(msg);
        if (next != null) return next.handle(level, msg);
        return "unhandled-calendar";
    }
    protected abstract boolean canHandle(int level);
    protected abstract String doHandle(String msg);
}

class CalendarLowHandler extends CalendarHandler {
    protected boolean canHandle(int level) { return level <= 1; }
    protected String doHandle(String msg) { return "low-calendar:" + msg; }
}

class CalendarHighHandler extends CalendarHandler {
    protected boolean canHandle(int level) { return level > 1; }
    protected String doHandle(String msg) { return "high-calendar:" + msg; }
}
