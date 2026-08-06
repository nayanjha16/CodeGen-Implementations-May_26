// DesignPatternsSolid | kind=design_pattern | label=chain of responsibility | domain=backup | tier=logging
package org.example.patterns;

public abstract class BackupHandler {
    protected BackupHandler next;
    public BackupHandler link(BackupHandler n) { next = n; return n; }
    public String handle(int level, String msg) {
        if (canHandle(level)) return doHandle(msg);
        if (next != null) return next.handle(level, msg);
        return "unhandled-backup";
    }
    protected abstract boolean canHandle(int level);
    protected abstract String doHandle(String msg);
}

class BackupLowHandler extends BackupHandler {
    protected boolean canHandle(int level) { return level <= 1; }
    protected String doHandle(String msg) { return "low-backup:" + msg; }
}

class BackupHighHandler extends BackupHandler {
    protected boolean canHandle(int level) { return level > 1; }
    protected String doHandle(String msg) { return "high-backup:" + msg; }
}
