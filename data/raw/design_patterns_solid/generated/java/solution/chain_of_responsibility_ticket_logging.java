// DesignPatternsSolid | kind=design_pattern | label=chain of responsibility | domain=ticket | tier=logging
package org.example.patterns;

public abstract class TicketHandler {
    protected TicketHandler next;
    public TicketHandler link(TicketHandler n) { next = n; return n; }
    public String handle(int level, String msg) {
        if (canHandle(level)) return doHandle(msg);
        if (next != null) return next.handle(level, msg);
        return "unhandled-ticket";
    }
    protected abstract boolean canHandle(int level);
    protected abstract String doHandle(String msg);
}

class TicketLowHandler extends TicketHandler {
    protected boolean canHandle(int level) { return level <= 1; }
    protected String doHandle(String msg) { return "low-ticket:" + msg; }
}

class TicketHighHandler extends TicketHandler {
    protected boolean canHandle(int level) { return level > 1; }
    protected String doHandle(String msg) { return "high-ticket:" + msg; }
}
