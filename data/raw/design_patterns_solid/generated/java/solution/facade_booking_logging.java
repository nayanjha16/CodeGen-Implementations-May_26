// DesignPatternsSolid | kind=design_pattern | label=facade | domain=booking | tier=logging
package org.example.patterns;

class BookingValidator {
    public boolean ok(String v) { return v != null && !v.isEmpty(); }
}
class BookingWriter {
    public String write(String v) { return "wrote-booking:" + v; }
}
public class BookingFacade {
    private final BookingValidator validator = new BookingValidator();
    private final BookingWriter writer = new BookingWriter();
    public String submit(String value) {
        if (!validator.ok(value)) return "invalid";
        return writer.write(value);
    }
}
