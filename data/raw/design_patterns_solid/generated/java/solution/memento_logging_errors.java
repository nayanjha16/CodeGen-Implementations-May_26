// DesignPatternsSolid | kind=design_pattern | label=memento | domain=logging | tier=errors
package org.example.patterns;

public class LoggingMemento {
    private final String state;
    public LoggingMemento(String state) { this.state = state; }
    public String getState() { return state; }
}

class LoggingOriginator {
    private String state = "logging-init";
    public void setState(String state) { this.state = state; }
    public String getState() { return state; }
    public LoggingMemento save() { return new LoggingMemento(state); }
    public void restore(LoggingMemento m) { this.state = m.getState(); }
}
