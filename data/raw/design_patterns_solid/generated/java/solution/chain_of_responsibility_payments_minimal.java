// DesignPatternsSolid | kind=design_pattern | label=chain of responsibility | domain=payments | tier=minimal
package org.example.patterns;

public abstract class PaymentsHandler {
    protected PaymentsHandler next;
    public PaymentsHandler link(PaymentsHandler n) { next = n; return n; }
    public String handle(int level, String msg) {
        if (canHandle(level)) return doHandle(msg);
        if (next != null) return next.handle(level, msg);
        return "unhandled-payments";
    }
    protected abstract boolean canHandle(int level);
    protected abstract String doHandle(String msg);
}

class PaymentsLowHandler extends PaymentsHandler {
    protected boolean canHandle(int level) { return level <= 1; }
    protected String doHandle(String msg) { return "low-payments:" + msg; }
}

class PaymentsHighHandler extends PaymentsHandler {
    protected boolean canHandle(int level) { return level > 1; }
    protected String doHandle(String msg) { return "high-payments:" + msg; }
}
