// DesignPatternsSolid | kind=design_pattern | label=chain of responsibility | domain=inventory | tier=minimal
package org.example.patterns;

public abstract class InventoryHandler {
    protected InventoryHandler next;
    public InventoryHandler link(InventoryHandler n) { next = n; return n; }
    public String handle(int level, String msg) {
        if (canHandle(level)) return doHandle(msg);
        if (next != null) return next.handle(level, msg);
        return "unhandled-inventory";
    }
    protected abstract boolean canHandle(int level);
    protected abstract String doHandle(String msg);
}

class InventoryLowHandler extends InventoryHandler {
    protected boolean canHandle(int level) { return level <= 1; }
    protected String doHandle(String msg) { return "low-inventory:" + msg; }
}

class InventoryHighHandler extends InventoryHandler {
    protected boolean canHandle(int level) { return level > 1; }
    protected String doHandle(String msg) { return "high-inventory:" + msg; }
}
