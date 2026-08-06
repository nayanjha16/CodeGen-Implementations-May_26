// DesignPatternsSolid | kind=design_pattern | label=template method | domain=booking | tier=minimal
package org.example.patterns;

public abstract class BookingTemplate {
    public final String run(String input) {
        String prepared = prepare(input);
        String processed = process(prepared);
        return finish(processed);
    }
    protected String prepare(String input) { return input.trim(); }
    protected abstract String process(String input);
    protected String finish(String input) { return "booking|" + input; }
}

class BookingUpperTemplate extends BookingTemplate {
    protected String process(String input) { return input.toUpperCase(); }
}
