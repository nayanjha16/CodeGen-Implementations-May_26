// DesignPatternsSolid | kind=design_pattern | label=bridge | domain=config | tier=errors
package org.example.patterns;

interface ConfigImpl {
    String write(String msg);
}

class ConfigFileImpl implements ConfigImpl {
    public String write(String msg) { return "file:config:" + msg; }
}

class ConfigMemoryImpl implements ConfigImpl {
    public String write(String msg) { return "mem:config:" + msg; }
}

public abstract class ConfigBridge {
    protected final ConfigImpl impl;
    protected ConfigBridge(ConfigImpl impl) { this.impl = impl; }
    public abstract String send(String msg);
}

class ConfigAlertBridge extends ConfigBridge {
    public ConfigAlertBridge(ConfigImpl impl) { super(impl); }
    public String send(String msg) { return impl.write("ALERT-" + msg); }
}
