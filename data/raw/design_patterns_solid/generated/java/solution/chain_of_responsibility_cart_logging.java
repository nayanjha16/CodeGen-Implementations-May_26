// DesignPatternsSolid | kind=design_pattern | label=chain of responsibility | domain=cart | tier=logging
package org.example.patterns;

public abstract class CartHandler {
    protected CartHandler next;
    public CartHandler link(CartHandler n) { next = n; return n; }
    public String handle(int level, String msg) {
        if (canHandle(level)) return doHandle(msg);
        if (next != null) return next.handle(level, msg);
        return "unhandled-cart";
    }
    protected abstract boolean canHandle(int level);
    protected abstract String doHandle(String msg);
}

class CartLowHandler extends CartHandler {
    protected boolean canHandle(int level) { return level <= 1; }
    protected String doHandle(String msg) { return "low-cart:" + msg; }
}

class CartHighHandler extends CartHandler {
    protected boolean canHandle(int level) { return level > 1; }
    protected String doHandle(String msg) { return "high-cart:" + msg; }
}
