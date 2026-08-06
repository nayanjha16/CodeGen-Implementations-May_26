// DesignPatternsSolid | kind=solid | label=srp | domain=search | tier=minimal
package org.example.patterns;

// SRP: separate persistence from formatting for search
class SearchRecord {
    public final String id;
    public final int amount;
    public SearchRecord(String id, int amount) { this.id = id; this.amount = amount; }
}

class SearchRepository {
    public String save(SearchRecord r) { return "saved-search:" + r.id; }
}

public class SearchFormatter {
    public String format(SearchRecord r) { return r.id + "=" + r.amount; }
}
