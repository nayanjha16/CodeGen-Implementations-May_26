// DesignPatternsSolid | kind=design_pattern | label=memento | domain=billing | tier=logging
package org.example.patterns;

public class BillingMemento {
    private final String state;
    public BillingMemento(String state) { this.state = state; }
    public String getState() { return state; }
}

class BillingOriginator {
    private String state = "billing-init";
    public void setState(String state) { this.state = state; }
    public String getState() { return state; }
    public BillingMemento save() { return new BillingMemento(state); }
    public void restore(BillingMemento m) { this.state = m.getState(); }
}
