// DesignPatternsSolid | kind=solid | label=srp | domain=report | tier=minimal
package org.example.patterns;

// SRP: separate persistence from formatting for report
class ReportRecord {
    public final String id;
    public final int amount;
    public ReportRecord(String id, int amount) { this.id = id; this.amount = amount; }
}

class ReportRepository {
    public String save(ReportRecord r) { return "saved-report:" + r.id; }
}

public class ReportFormatter {
    public String format(ReportRecord r) { return r.id + "=" + r.amount; }
}
