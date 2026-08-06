// DesignPatternsSolid | kind=design_pattern | label=bridge | domain=backup | tier=logging
package org.example.patterns;

interface BackupImpl {
    String write(String msg);
}

class BackupFileImpl implements BackupImpl {
    public String write(String msg) { return "file:backup:" + msg; }
}

class BackupMemoryImpl implements BackupImpl {
    public String write(String msg) { return "mem:backup:" + msg; }
}

public abstract class BackupBridge {
    protected final BackupImpl impl;
    protected BackupBridge(BackupImpl impl) { this.impl = impl; }
    public abstract String send(String msg);
}

class BackupAlertBridge extends BackupBridge {
    public BackupAlertBridge(BackupImpl impl) { super(impl); }
    public String send(String msg) { return impl.write("ALERT-" + msg); }
}
