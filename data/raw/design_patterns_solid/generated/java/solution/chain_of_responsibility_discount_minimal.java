// DesignPatternsSolid | kind=design_pattern | label=chain of responsibility | domain=discount | tier=minimal
package org.example.patterns;

public abstract class DiscountHandler {
    protected DiscountHandler next;
    public DiscountHandler link(DiscountHandler n) { next = n; return n; }
    public String handle(int level, String msg) {
        if (canHandle(level)) return doHandle(msg);
        if (next != null) return next.handle(level, msg);
        return "unhandled-discount";
    }
    protected abstract boolean canHandle(int level);
    protected abstract String doHandle(String msg);
}

class DiscountLowHandler extends DiscountHandler {
    protected boolean canHandle(int level) { return level <= 1; }
    protected String doHandle(String msg) { return "low-discount:" + msg; }
}

class DiscountHighHandler extends DiscountHandler {
    protected boolean canHandle(int level) { return level > 1; }
    protected String doHandle(String msg) { return "high-discount:" + msg; }
}
