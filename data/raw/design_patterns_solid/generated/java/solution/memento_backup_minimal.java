// DesignPatternsSolid | kind=design_pattern | label=memento | domain=backup | tier=minimal
package org.example.patterns;

public class BackupMemento {
    private final String state;
    public BackupMemento(String state) { this.state = state; }
    public String getState() { return state; }
}

class BackupOriginator {
    private String state = "backup-init";
    public void setState(String state) { this.state = state; }
    public String getState() { return state; }
    public BackupMemento save() { return new BackupMemento(state); }
    public void restore(BackupMemento m) { this.state = m.getState(); }
}
