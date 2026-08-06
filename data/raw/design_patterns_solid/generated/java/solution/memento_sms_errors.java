// DesignPatternsSolid | kind=design_pattern | label=memento | domain=sms | tier=errors
package org.example.patterns;

public class SmsMemento {
    private final String state;
    public SmsMemento(String state) { this.state = state; }
    public String getState() { return state; }
}

class SmsOriginator {
    private String state = "sms-init";
    public void setState(String state) { this.state = state; }
    public String getState() { return state; }
    public SmsMemento save() { return new SmsMemento(state); }
    public void restore(SmsMemento m) { this.state = m.getState(); }
}
