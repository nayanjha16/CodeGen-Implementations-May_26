// DesignPatternsSolid | kind=solid | label=srp | domain=metrics | tier=logging
package org.example.patterns;

// SRP: separate persistence from formatting for metrics
class MetricsRecord {
    public final String id;
    public final int amount;
    public MetricsRecord(String id, int amount) { this.id = id; this.amount = amount; }
}

class MetricsRepository {
    public String save(MetricsRecord r) { return "saved-metrics:" + r.id; }
}

public class MetricsFormatter {
    public String format(MetricsRecord r) { return r.id + "=" + r.amount; }
}
