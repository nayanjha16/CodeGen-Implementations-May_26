// DesignPatternsSolid | kind=design_pattern | label=memento | domain=editor | tier=minimal
package org.example.patterns;

public class EditorMemento {
    private final String state;
    public EditorMemento(String state) { this.state = state; }
    public String getState() { return state; }
}

class EditorOriginator {
    private String state = "editor-init";
    public void setState(String state) { this.state = state; }
    public String getState() { return state; }
    public EditorMemento save() { return new EditorMemento(state); }
    public void restore(EditorMemento m) { this.state = m.getState(); }
}
