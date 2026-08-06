// DesignPatternsSolid | kind=design_pattern | label=memento | domain=auth | tier=logging
package org.example.patterns;

public class AuthMemento {
    private final String state;
    public AuthMemento(String state) { this.state = state; }
    public String getState() { return state; }
}

class AuthOriginator {
    private String state = "auth-init";
    public void setState(String state) { this.state = state; }
    public String getState() { return state; }
    public AuthMemento save() { return new AuthMemento(state); }
    public void restore(AuthMemento m) { this.state = m.getState(); }
}
