// DesignPatternsSolid | kind=design_pattern | label=chain of responsibility | domain=notes | tier=logging
package org.example.patterns;

public abstract class NotesHandler {
    protected NotesHandler next;
    public NotesHandler link(NotesHandler n) { next = n; return n; }
    public String handle(int level, String msg) {
        if (canHandle(level)) return doHandle(msg);
        if (next != null) return next.handle(level, msg);
        return "unhandled-notes";
    }
    protected abstract boolean canHandle(int level);
    protected abstract String doHandle(String msg);
}

class NotesLowHandler extends NotesHandler {
    protected boolean canHandle(int level) { return level <= 1; }
    protected String doHandle(String msg) { return "low-notes:" + msg; }
}

class NotesHighHandler extends NotesHandler {
    protected boolean canHandle(int level) { return level > 1; }
    protected String doHandle(String msg) { return "high-notes:" + msg; }
}
