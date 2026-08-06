// DesignPatternsSolid | kind=design_pattern | label=bridge | domain=tax | tier=minimal
package org.example.patterns;

interface TaxImpl {
    String write(String msg);
}

class TaxFileImpl implements TaxImpl {
    public String write(String msg) { return "file:tax:" + msg; }
}

class TaxMemoryImpl implements TaxImpl {
    public String write(String msg) { return "mem:tax:" + msg; }
}

public abstract class TaxBridge {
    protected final TaxImpl impl;
    protected TaxBridge(TaxImpl impl) { this.impl = impl; }
    public abstract String send(String msg);
}

class TaxAlertBridge extends TaxBridge {
    public TaxAlertBridge(TaxImpl impl) { super(impl); }
    public String send(String msg) { return impl.write("ALERT-" + msg); }
}
