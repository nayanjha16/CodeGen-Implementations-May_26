// DesignPatternsSolid | kind=solid | label=srp | domain=sms | tier=minimal
package org.example.patterns;

// SRP: separate persistence from formatting for sms
class SmsRecord {
    public final String id;
    public final int amount;
    public SmsRecord(String id, int amount) { this.id = id; this.amount = amount; }
}

class SmsRepository {
    public String save(SmsRecord r) { return "saved-sms:" + r.id; }
}

public class SmsFormatter {
    public String format(SmsRecord r) { return r.id + "=" + r.amount; }
}
