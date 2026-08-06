// DesignPatternsSolid | kind=design_pattern | label=chain of responsibility | domain=todo | tier=errors
package org.example.patterns;

public abstract class TodoHandler {
    protected TodoHandler next;
    public TodoHandler link(TodoHandler n) { next = n; return n; }
    public String handle(int level, String msg) {
        if (canHandle(level)) return doHandle(msg);
        if (next != null) return next.handle(level, msg);
        return "unhandled-todo";
    }
    protected abstract boolean canHandle(int level);
    protected abstract String doHandle(String msg);
}

class TodoLowHandler extends TodoHandler {
    protected boolean canHandle(int level) { return level <= 1; }
    protected String doHandle(String msg) { return "low-todo:" + msg; }
}

class TodoHighHandler extends TodoHandler {
    protected boolean canHandle(int level) { return level > 1; }
    protected String doHandle(String msg) { return "high-todo:" + msg; }
}
