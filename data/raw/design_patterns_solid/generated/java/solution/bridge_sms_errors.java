// DesignPatternsSolid | kind=design_pattern | label=bridge | domain=sms | tier=errors
package org.example.patterns;

interface SmsImpl {
    String write(String msg);
}

class SmsFileImpl implements SmsImpl {
    public String write(String msg) { return "file:sms:" + msg; }
}

class SmsMemoryImpl implements SmsImpl {
    public String write(String msg) { return "mem:sms:" + msg; }
}

public abstract class SmsBridge {
    protected final SmsImpl impl;
    protected SmsBridge(SmsImpl impl) { this.impl = impl; }
    public abstract String send(String msg);
}

class SmsAlertBridge extends SmsBridge {
    public SmsAlertBridge(SmsImpl impl) { super(impl); }
    public String send(String msg) { return impl.write("ALERT-" + msg); }
}
