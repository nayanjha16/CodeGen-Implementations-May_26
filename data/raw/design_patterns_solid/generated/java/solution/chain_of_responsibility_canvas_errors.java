// DesignPatternsSolid | kind=design_pattern | label=chain of responsibility | domain=canvas | tier=errors
package org.example.patterns;

public abstract class CanvasHandler {
    protected CanvasHandler next;
    public CanvasHandler link(CanvasHandler n) { next = n; return n; }
    public String handle(int level, String msg) {
        if (canHandle(level)) return doHandle(msg);
        if (next != null) return next.handle(level, msg);
        return "unhandled-canvas";
    }
    protected abstract boolean canHandle(int level);
    protected abstract String doHandle(String msg);
}

class CanvasLowHandler extends CanvasHandler {
    protected boolean canHandle(int level) { return level <= 1; }
    protected String doHandle(String msg) { return "low-canvas:" + msg; }
}

class CanvasHighHandler extends CanvasHandler {
    protected boolean canHandle(int level) { return level > 1; }
    protected String doHandle(String msg) { return "high-canvas:" + msg; }
}
