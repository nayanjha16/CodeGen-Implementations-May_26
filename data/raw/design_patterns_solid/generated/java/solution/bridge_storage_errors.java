// DesignPatternsSolid | kind=design_pattern | label=bridge | domain=storage | tier=errors
package org.example.patterns;

interface StorageImpl {
    String write(String msg);
}

class StorageFileImpl implements StorageImpl {
    public String write(String msg) { return "file:storage:" + msg; }
}

class StorageMemoryImpl implements StorageImpl {
    public String write(String msg) { return "mem:storage:" + msg; }
}

public abstract class StorageBridge {
    protected final StorageImpl impl;
    protected StorageBridge(StorageImpl impl) { this.impl = impl; }
    public abstract String send(String msg);
}

class StorageAlertBridge extends StorageBridge {
    public StorageAlertBridge(StorageImpl impl) { super(impl); }
    public String send(String msg) { return impl.write("ALERT-" + msg); }
}
