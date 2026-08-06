// DesignPatternsSolid | kind=solid | label=srp | domain=sensors | tier=minimal
package org.example.patterns;

// SRP: separate persistence from formatting for sensors
class SensorsRecord {
    public final String id;
    public final int amount;
    public SensorsRecord(String id, int amount) { this.id = id; this.amount = amount; }
}

class SensorsRepository {
    public String save(SensorsRecord r) { return "saved-sensors:" + r.id; }
}

public class SensorsFormatter {
    public String format(SensorsRecord r) { return r.id + "=" + r.amount; }
}
