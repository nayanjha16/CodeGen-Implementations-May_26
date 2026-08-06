// DesignPatternsSolid | kind=design_pattern | label=memento | domain=notes | tier=logging
package org.example.patterns;

public class NotesMemento {
    private final String state;
    public NotesMemento(String state) { this.state = state; }
    public String getState() { return state; }
}

class NotesOriginator {
    private String state = "notes-init";
    public void setState(String state) { this.state = state; }
    public String getState() { return state; }
    public NotesMemento save() { return new NotesMemento(state); }
    public void restore(NotesMemento m) { this.state = m.getState(); }
}
