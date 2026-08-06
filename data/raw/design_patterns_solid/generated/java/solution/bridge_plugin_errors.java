// DesignPatternsSolid | kind=design_pattern | label=bridge | domain=plugin | tier=errors
package org.example.patterns;

interface PluginImpl {
    String write(String msg);
}

class PluginFileImpl implements PluginImpl {
    public String write(String msg) { return "file:plugin:" + msg; }
}

class PluginMemoryImpl implements PluginImpl {
    public String write(String msg) { return "mem:plugin:" + msg; }
}

public abstract class PluginBridge {
    protected final PluginImpl impl;
    protected PluginBridge(PluginImpl impl) { this.impl = impl; }
    public abstract String send(String msg);
}

class PluginAlertBridge extends PluginBridge {
    public PluginAlertBridge(PluginImpl impl) { super(impl); }
    public String send(String msg) { return impl.write("ALERT-" + msg); }
}
