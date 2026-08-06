// DesignPatternsSolid | kind=solid | label=srp | domain=canvas | tier=minimal
package org.example.patterns;

// SRP: separate persistence from formatting for canvas
class CanvasRecord {
    public final String id;
    public final int amount;
    public CanvasRecord(String id, int amount) { this.id = id; this.amount = amount; }
}

class CanvasRepository {
    public String save(CanvasRecord r) { return "saved-canvas:" + r.id; }
}

public class CanvasFormatter {
    public String format(CanvasRecord r) { return r.id + "=" + r.amount; }
}
