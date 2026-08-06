// DesignPatternsSolid | kind=design_pattern | label=bridge | domain=discount | tier=errors
package org.example.patterns;

interface DiscountImpl {
    String write(String msg);
}

class DiscountFileImpl implements DiscountImpl {
    public String write(String msg) { return "file:discount:" + msg; }
}

class DiscountMemoryImpl implements DiscountImpl {
    public String write(String msg) { return "mem:discount:" + msg; }
}

public abstract class DiscountBridge {
    protected final DiscountImpl impl;
    protected DiscountBridge(DiscountImpl impl) { this.impl = impl; }
    public abstract String send(String msg);
}

class DiscountAlertBridge extends DiscountBridge {
    public DiscountAlertBridge(DiscountImpl impl) { super(impl); }
    public String send(String msg) { return impl.write("ALERT-" + msg); }
}
