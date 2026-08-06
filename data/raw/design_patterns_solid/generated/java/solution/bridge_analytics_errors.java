// DesignPatternsSolid | kind=design_pattern | label=bridge | domain=analytics | tier=errors
package org.example.patterns;

interface AnalyticsImpl {
    String write(String msg);
}

class AnalyticsFileImpl implements AnalyticsImpl {
    public String write(String msg) { return "file:analytics:" + msg; }
}

class AnalyticsMemoryImpl implements AnalyticsImpl {
    public String write(String msg) { return "mem:analytics:" + msg; }
}

public abstract class AnalyticsBridge {
    protected final AnalyticsImpl impl;
    protected AnalyticsBridge(AnalyticsImpl impl) { this.impl = impl; }
    public abstract String send(String msg);
}

class AnalyticsAlertBridge extends AnalyticsBridge {
    public AnalyticsAlertBridge(AnalyticsImpl impl) { super(impl); }
    public String send(String msg) { return impl.write("ALERT-" + msg); }
}
