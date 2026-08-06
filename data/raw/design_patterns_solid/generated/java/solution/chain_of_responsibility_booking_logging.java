// DesignPatternsSolid | kind=design_pattern | label=chain of responsibility | domain=booking | tier=logging
package org.example.patterns;

public abstract class BookingHandler {
    protected BookingHandler next;
    public BookingHandler link(BookingHandler n) { next = n; return n; }
    public String handle(int level, String msg) {
        if (canHandle(level)) return doHandle(msg);
        if (next != null) return next.handle(level, msg);
        return "unhandled-booking";
    }
    protected abstract boolean canHandle(int level);
    protected abstract String doHandle(String msg);
}

class BookingLowHandler extends BookingHandler {
    protected boolean canHandle(int level) { return level <= 1; }
    protected String doHandle(String msg) { return "low-booking:" + msg; }
}

class BookingHighHandler extends BookingHandler {
    protected boolean canHandle(int level) { return level > 1; }
    protected String doHandle(String msg) { return "high-booking:" + msg; }
}
