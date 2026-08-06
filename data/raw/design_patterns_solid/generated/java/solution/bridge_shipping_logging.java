// DesignPatternsSolid | kind=design_pattern | label=bridge | domain=shipping | tier=logging
package org.example.patterns;

interface ShippingImpl {
    String write(String msg);
}

class ShippingFileImpl implements ShippingImpl {
    public String write(String msg) { return "file:shipping:" + msg; }
}

class ShippingMemoryImpl implements ShippingImpl {
    public String write(String msg) { return "mem:shipping:" + msg; }
}

public abstract class ShippingBridge {
    protected final ShippingImpl impl;
    protected ShippingBridge(ShippingImpl impl) { this.impl = impl; }
    public abstract String send(String msg);
}

class ShippingAlertBridge extends ShippingBridge {
    public ShippingAlertBridge(ShippingImpl impl) { super(impl); }
    public String send(String msg) { return impl.write("ALERT-" + msg); }
}
