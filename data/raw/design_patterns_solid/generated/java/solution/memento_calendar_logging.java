// DesignPatternsSolid | kind=design_pattern | label=memento | domain=calendar | tier=logging
package org.example.patterns;

public class CalendarMemento {
    private final String state;
    public CalendarMemento(String state) { this.state = state; }
    public String getState() { return state; }
}

class CalendarOriginator {
    private String state = "calendar-init";
    public void setState(String state) { this.state = state; }
    public String getState() { return state; }
    public CalendarMemento save() { return new CalendarMemento(state); }
    public void restore(CalendarMemento m) { this.state = m.getState(); }
}
