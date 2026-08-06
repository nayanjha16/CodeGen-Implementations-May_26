// DesignPatternsSolid | kind=design_pattern | label=command | domain=map | tier=logging
package org.example.patterns;

interface MapCommand {
    String execute();
}

class MapReceiver {
    public String action(String x) { return "done-map:" + x; }
}

public class MapActionCommand implements MapCommand {
    private final MapReceiver receiver;
    private final String payload;
    public MapActionCommand(MapReceiver r, String payload) {
        this.receiver = r; this.payload = payload;
    }
    public String execute() { return receiver.action(payload); }
}
