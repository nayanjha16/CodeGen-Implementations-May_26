// DesignPatternsSolid | kind=design_pattern | label=bridge | domain=cache | tier=minimal
package org.example.patterns;

interface CacheImpl {
    String write(String msg);
}

class CacheFileImpl implements CacheImpl {
    public String write(String msg) { return "file:cache:" + msg; }
}

class CacheMemoryImpl implements CacheImpl {
    public String write(String msg) { return "mem:cache:" + msg; }
}

public abstract class CacheBridge {
    protected final CacheImpl impl;
    protected CacheBridge(CacheImpl impl) { this.impl = impl; }
    public abstract String send(String msg);
}

class CacheAlertBridge extends CacheBridge {
    public CacheAlertBridge(CacheImpl impl) { super(impl); }
    public String send(String msg) { return impl.write("ALERT-" + msg); }
}
