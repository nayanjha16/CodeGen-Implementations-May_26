// DesignPatternsSolid | kind=solid | label=srp | domain=inventory | tier=logging
package org.example.patterns;

// SRP: separate persistence from formatting for inventory
class InventoryRecord {
    public final String id;
    public final int amount;
    public InventoryRecord(String id, int amount) { this.id = id; this.amount = amount; }
}

class InventoryRepository {
    public String save(InventoryRecord r) { return "saved-inventory:" + r.id; }
}

public class InventoryFormatter {
    public String format(InventoryRecord r) { return r.id + "=" + r.amount; }
}
