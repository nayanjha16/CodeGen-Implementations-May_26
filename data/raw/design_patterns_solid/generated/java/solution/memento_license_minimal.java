// DesignPatternsSolid | kind=design_pattern | label=memento | domain=license | tier=minimal
package org.example.patterns;

public class LicenseMemento {
    private final String state;
    public LicenseMemento(String state) { this.state = state; }
    public String getState() { return state; }
}

class LicenseOriginator {
    private String state = "license-init";
    public void setState(String state) { this.state = state; }
    public String getState() { return state; }
    public LicenseMemento save() { return new LicenseMemento(state); }
    public void restore(LicenseMemento m) { this.state = m.getState(); }
}
