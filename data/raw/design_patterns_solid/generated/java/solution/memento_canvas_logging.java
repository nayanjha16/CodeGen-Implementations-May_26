// DesignPatternsSolid | kind=design_pattern | label=memento | domain=canvas | tier=logging
package org.example.patterns;

public class CanvasMemento {
    private final String state;
    public CanvasMemento(String state) { this.state = state; }
    public String getState() { return state; }
}

class CanvasOriginator {
    private String state = "canvas-init";
    public void setState(String state) { this.state = state; }
    public String getState() { return state; }
    public CanvasMemento save() { return new CanvasMemento(state); }
    public void restore(CanvasMemento m) { this.state = m.getState(); }
}
