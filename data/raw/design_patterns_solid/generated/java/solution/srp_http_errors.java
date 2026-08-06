// DesignPatternsSolid | kind=solid | label=srp | domain=http | tier=errors
package org.example.patterns;

// SRP: separate persistence from formatting for http
class HttpRecord {
    public final String id;
    public final int amount;
    public HttpRecord(String id, int amount) { this.id = id; this.amount = amount; }
}

class HttpRepository {
    public String save(HttpRecord r) { return "saved-http:" + r.id; }
}

public class HttpFormatter {
    public String format(HttpRecord r) { return r.id + "=" + r.amount; }
}
