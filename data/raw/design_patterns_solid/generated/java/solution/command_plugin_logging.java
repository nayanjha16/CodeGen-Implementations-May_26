// DesignPatternsSolid | kind=design_pattern | label=command | domain=plugin | tier=logging
package org.example.patterns;

interface PluginCommand {
    String execute();
}

class PluginReceiver {
    public String action(String x) { return "done-plugin:" + x; }
}

public class PluginActionCommand implements PluginCommand {
    private final PluginReceiver receiver;
    private final String payload;
    public PluginActionCommand(PluginReceiver r, String payload) {
        this.receiver = r; this.payload = payload;
    }
    public String execute() { return receiver.action(payload); }
}
