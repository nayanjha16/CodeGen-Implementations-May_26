// DesignPatternsSolid | kind=solid | label=srp | domain=cache | tier=errors
package org.example.patterns;

// SRP: separate persistence from formatting for cache
class CacheRecord {
    public final String id;
    public final int amount;
    public CacheRecord(String id, int amount) { this.id = id; this.amount = amount; }
}

class CacheRepository {
    public String save(CacheRecord r) { return "saved-cache:" + r.id; }
}

public class CacheFormatter {
    public String format(CacheRecord r) { return r.id + "=" + r.amount; }
}
