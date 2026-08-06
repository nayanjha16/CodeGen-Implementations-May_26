// DesignPatternsSolid | kind=design_pattern | label=chain of responsibility | domain=billing | tier=minimal
package org.example.patterns;

public abstract class BillingHandler {
    protected BillingHandler next;
    public BillingHandler link(BillingHandler n) { next = n; return n; }
    public String handle(int level, String msg) {
        if (canHandle(level)) return doHandle(msg);
        if (next != null) return next.handle(level, msg);
        return "unhandled-billing";
    }
    protected abstract boolean canHandle(int level);
    protected abstract String doHandle(String msg);
}

class BillingLowHandler extends BillingHandler {
    protected boolean canHandle(int level) { return level <= 1; }
    protected String doHandle(String msg) { return "low-billing:" + msg; }
}

class BillingHighHandler extends BillingHandler {
    protected boolean canHandle(int level) { return level > 1; }
    protected String doHandle(String msg) { return "high-billing:" + msg; }
}
