// DesignPatternsSolid | kind=design_pattern | label=command | domain=config | tier=errors
package org.example.patterns;

interface ConfigCommand {
    String execute();
}

class ConfigReceiver {
    public String action(String x) { return "done-config:" + x; }
}

public class ConfigActionCommand implements ConfigCommand {
    private final ConfigReceiver receiver;
    private final String payload;
    public ConfigActionCommand(ConfigReceiver r, String payload) {
        this.receiver = r; this.payload = payload;
    }
    public String execute() { return receiver.action(payload); }
}
