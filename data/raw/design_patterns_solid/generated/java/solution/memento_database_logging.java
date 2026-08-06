// DesignPatternsSolid | kind=design_pattern | label=memento | domain=database | tier=logging
package org.example.patterns;

public class DatabaseMemento {
    private final String state;
    public DatabaseMemento(String state) { this.state = state; }
    public String getState() { return state; }
}

class DatabaseOriginator {
    private String state = "database-init";
    public void setState(String state) { this.state = state; }
    public String getState() { return state; }
    public DatabaseMemento save() { return new DatabaseMemento(state); }
    public void restore(DatabaseMemento m) { this.state = m.getState(); }
}
