// DesignPatternsSolid | kind=design_pattern | label=chain of responsibility | domain=shipping | tier=minimal
package org.example.patterns;

public abstract class ShippingHandler {
    protected ShippingHandler next;
    public ShippingHandler link(ShippingHandler n) { next = n; return n; }
    public String handle(int level, String msg) {
        if (canHandle(level)) return doHandle(msg);
        if (next != null) return next.handle(level, msg);
        return "unhandled-shipping";
    }
    protected abstract boolean canHandle(int level);
    protected abstract String doHandle(String msg);
}

class ShippingLowHandler extends ShippingHandler {
    protected boolean canHandle(int level) { return level <= 1; }
    protected String doHandle(String msg) { return "low-shipping:" + msg; }
}

class ShippingHighHandler extends ShippingHandler {
    protected boolean canHandle(int level) { return level > 1; }
    protected String doHandle(String msg) { return "high-shipping:" + msg; }
}
