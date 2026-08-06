// DesignPatternsSolid | kind=design_pattern | label=memento | domain=payments | tier=logging
package org.example.patterns;

public class PaymentsMemento {
    private final String state;
    public PaymentsMemento(String state) { this.state = state; }
    public String getState() { return state; }
}

class PaymentsOriginator {
    private String state = "payments-init";
    public void setState(String state) { this.state = state; }
    public String getState() { return state; }
    public PaymentsMemento save() { return new PaymentsMemento(state); }
    public void restore(PaymentsMemento m) { this.state = m.getState(); }
}
