// DesignPatternsSolid | kind=design_pattern | label=bridge | domain=wallet | tier=minimal
package org.example.patterns;

interface WalletImpl {
    String write(String msg);
}

class WalletFileImpl implements WalletImpl {
    public String write(String msg) { return "file:wallet:" + msg; }
}

class WalletMemoryImpl implements WalletImpl {
    public String write(String msg) { return "mem:wallet:" + msg; }
}

public abstract class WalletBridge {
    protected final WalletImpl impl;
    protected WalletBridge(WalletImpl impl) { this.impl = impl; }
    public abstract String send(String msg);
}

class WalletAlertBridge extends WalletBridge {
    public WalletAlertBridge(WalletImpl impl) { super(impl); }
    public String send(String msg) { return impl.write("ALERT-" + msg); }
}
