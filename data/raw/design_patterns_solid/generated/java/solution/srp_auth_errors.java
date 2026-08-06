// DesignPatternsSolid | kind=solid | label=srp | domain=auth | tier=errors
package org.example.patterns;

// SRP: separate persistence from formatting for auth
class AuthRecord {
    public final String id;
    public final int amount;
    public AuthRecord(String id, int amount) { this.id = id; this.amount = amount; }
}

class AuthRepository {
    public String save(AuthRecord r) { return "saved-auth:" + r.id; }
}

public class AuthFormatter {
    public String format(AuthRecord r) { return r.id + "=" + r.amount; }
}
