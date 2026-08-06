// DesignPatternsSolid | kind=design_pattern | label=bridge | domain=cart | tier=minimal
package org.example.patterns;

interface CartImpl {
    String write(String msg);
}

class CartFileImpl implements CartImpl {
    public String write(String msg) { return "file:cart:" + msg; }
}

class CartMemoryImpl implements CartImpl {
    public String write(String msg) { return "mem:cart:" + msg; }
}

public abstract class CartBridge {
    protected final CartImpl impl;
    protected CartBridge(CartImpl impl) { this.impl = impl; }
    public abstract String send(String msg);
}

class CartAlertBridge extends CartBridge {
    public CartAlertBridge(CartImpl impl) { super(impl); }
    public String send(String msg) { return impl.write("ALERT-" + msg); }
}
