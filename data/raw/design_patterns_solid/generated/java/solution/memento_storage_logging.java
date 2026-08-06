// DesignPatternsSolid | kind=design_pattern | label=memento | domain=storage | tier=logging
package org.example.patterns;

public class StorageMemento {
    private final String state;
    public StorageMemento(String state) { this.state = state; }
    public String getState() { return state; }
}

class StorageOriginator {
    private String state = "storage-init";
    public void setState(String state) { this.state = state; }
    public String getState() { return state; }
    public StorageMemento save() { return new StorageMemento(state); }
    public void restore(StorageMemento m) { this.state = m.getState(); }
}
