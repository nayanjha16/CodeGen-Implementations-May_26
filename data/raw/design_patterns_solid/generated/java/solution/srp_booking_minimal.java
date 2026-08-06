// DesignPatternsSolid | kind=solid | label=srp | domain=booking | tier=minimal
package org.example.patterns;

// SRP: separate persistence from formatting for booking
class BookingRecord {
    public final String id;
    public final int amount;
    public BookingRecord(String id, int amount) { this.id = id; this.amount = amount; }
}

class BookingRepository {
    public String save(BookingRecord r) { return "saved-booking:" + r.id; }
}

public class BookingFormatter {
    public String format(BookingRecord r) { return r.id + "=" + r.amount; }
}
