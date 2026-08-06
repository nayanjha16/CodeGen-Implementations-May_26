// DesignPatternsSolid | kind=design_pattern | label=memento | domain=notifications | tier=errors
package org.example.patterns;

public class NotificationsMemento {
    private final String state;
    public NotificationsMemento(String state) { this.state = state; }
    public String getState() { return state; }
}

class NotificationsOriginator {
    private String state = "notifications-init";
    public void setState(String state) { this.state = state; }
    public String getState() { return state; }
    public NotificationsMemento save() { return new NotificationsMemento(state); }
    public void restore(NotificationsMemento m) { this.state = m.getState(); }
}
