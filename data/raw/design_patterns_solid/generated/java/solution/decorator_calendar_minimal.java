// DesignPatternsSolid | kind=design_pattern | label=decorator | domain=calendar | tier=minimal
package org.example.patterns;

interface CalendarComponent {
    String process(String input);
}

class CalendarCore implements CalendarComponent {
    public String process(String input) { return "calendar:" + input; }
}

public class CalendarUpperDecorator implements CalendarComponent {
    private final CalendarComponent inner;
    public CalendarUpperDecorator(CalendarComponent inner) { this.inner = inner; }
    public String process(String input) {
        return inner.process(input).toUpperCase();
    }
}
