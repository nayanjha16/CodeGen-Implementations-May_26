// DesignPatternsSolid | kind=design_pattern | label=memento | domain=session | tier=minimal
package org.example.patterns;

public class SessionMemento {
    private final String state;
    public SessionMemento(String state) { this.state = state; }
    public String getState() { return state; }
}

class SessionOriginator {
    private String state = "session-init";
    public void setState(String state) { this.state = state; }
    public String getState() { return state; }
    public SessionMemento save() { return new SessionMemento(state); }
    public void restore(SessionMemento m) { this.state = m.getState(); }
}
