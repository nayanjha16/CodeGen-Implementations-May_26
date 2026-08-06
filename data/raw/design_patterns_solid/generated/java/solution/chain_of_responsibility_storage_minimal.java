// DesignPatternsSolid | kind=design_pattern | label=chain of responsibility | domain=storage | tier=minimal
package org.example.patterns;

public abstract class StorageHandler {
    protected StorageHandler next;
    public StorageHandler link(StorageHandler n) { next = n; return n; }
    public String handle(int level, String msg) {
        if (canHandle(level)) return doHandle(msg);
        if (next != null) return next.handle(level, msg);
        return "unhandled-storage";
    }
    protected abstract boolean canHandle(int level);
    protected abstract String doHandle(String msg);
}

class StorageLowHandler extends StorageHandler {
    protected boolean canHandle(int level) { return level <= 1; }
    protected String doHandle(String msg) { return "low-storage:" + msg; }
}

class StorageHighHandler extends StorageHandler {
    protected boolean canHandle(int level) { return level > 1; }
    protected String doHandle(String msg) { return "high-storage:" + msg; }
}
