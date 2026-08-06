// DesignPatternsSolid | kind=design_pattern | label=chain of responsibility | domain=game | tier=minimal
package org.example.patterns;

public abstract class GameHandler {
    protected GameHandler next;
    public GameHandler link(GameHandler n) { next = n; return n; }
    public String handle(int level, String msg) {
        if (canHandle(level)) return doHandle(msg);
        if (next != null) return next.handle(level, msg);
        return "unhandled-game";
    }
    protected abstract boolean canHandle(int level);
    protected abstract String doHandle(String msg);
}

class GameLowHandler extends GameHandler {
    protected boolean canHandle(int level) { return level <= 1; }
    protected String doHandle(String msg) { return "low-game:" + msg; }
}

class GameHighHandler extends GameHandler {
    protected boolean canHandle(int level) { return level > 1; }
    protected String doHandle(String msg) { return "high-game:" + msg; }
}
