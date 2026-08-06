// DesignPatternsSolid | kind=design_pattern | label=bridge | domain=sync | tier=logging
package org.example.patterns;

interface SyncImpl {
    String write(String msg);
}

class SyncFileImpl implements SyncImpl {
    public String write(String msg) { return "file:sync:" + msg; }
}

class SyncMemoryImpl implements SyncImpl {
    public String write(String msg) { return "mem:sync:" + msg; }
}

public abstract class SyncBridge {
    protected final SyncImpl impl;
    protected SyncBridge(SyncImpl impl) { this.impl = impl; }
    public abstract String send(String msg);
}

class SyncAlertBridge extends SyncBridge {
    public SyncAlertBridge(SyncImpl impl) { super(impl); }
    public String send(String msg) { return impl.write("ALERT-" + msg); }
}
