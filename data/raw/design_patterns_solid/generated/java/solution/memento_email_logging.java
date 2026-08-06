// DesignPatternsSolid | kind=design_pattern | label=memento | domain=email | tier=logging
package org.example.patterns;

public class EmailMemento {
    private final String state;
    public EmailMemento(String state) { this.state = state; }
    public String getState() { return state; }
}

class EmailOriginator {
    private String state = "email-init";
    public void setState(String state) { this.state = state; }
    public String getState() { return state; }
    public EmailMemento save() { return new EmailMemento(state); }
    public void restore(EmailMemento m) { this.state = m.getState(); }
}
