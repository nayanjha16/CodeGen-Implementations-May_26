// DesignPatternsSolid | kind=design_pattern | label=memento | domain=sensors | tier=errors
package org.example.patterns;

public class SensorsMemento {
    private final String state;
    public SensorsMemento(String state) { this.state = state; }
    public String getState() { return state; }
}

class SensorsOriginator {
    private String state = "sensors-init";
    public void setState(String state) { this.state = state; }
    public String getState() { return state; }
    public SensorsMemento save() { return new SensorsMemento(state); }
    public void restore(SensorsMemento m) { this.state = m.getState(); }
}
