// DesignPatternsSolid | kind=design_pattern | label=bridge | domain=payments | tier=minimal
package org.example.patterns;

interface PaymentsImpl {
    String write(String msg);
}

class PaymentsFileImpl implements PaymentsImpl {
    public String write(String msg) { return "file:payments:" + msg; }
}

class PaymentsMemoryImpl implements PaymentsImpl {
    public String write(String msg) { return "mem:payments:" + msg; }
}

public abstract class PaymentsBridge {
    protected final PaymentsImpl impl;
    protected PaymentsBridge(PaymentsImpl impl) { this.impl = impl; }
    public abstract String send(String msg);
}

class PaymentsAlertBridge extends PaymentsBridge {
    public PaymentsAlertBridge(PaymentsImpl impl) { super(impl); }
    public String send(String msg) { return impl.write("ALERT-" + msg); }
}
