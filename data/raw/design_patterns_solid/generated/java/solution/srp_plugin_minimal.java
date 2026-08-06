// DesignPatternsSolid | kind=solid | label=srp | domain=plugin | tier=minimal
package org.example.patterns;

// SRP: separate persistence from formatting for plugin
class PluginRecord {
    public final String id;
    public final int amount;
    public PluginRecord(String id, int amount) { this.id = id; this.amount = amount; }
}

class PluginRepository {
    public String save(PluginRecord r) { return "saved-plugin:" + r.id; }
}

public class PluginFormatter {
    public String format(PluginRecord r) { return r.id + "=" + r.amount; }
}
