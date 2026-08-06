// DesignPatternsSolid | kind=design_pattern | label=memento | domain=todo | tier=errors
package org.example.patterns;

public class TodoMemento {
    private final String state;
    public TodoMemento(String state) { this.state = state; }
    public String getState() { return state; }
}

class TodoOriginator {
    private String state = "todo-init";
    public void setState(String state) { this.state = state; }
    public String getState() { return state; }
    public TodoMemento save() { return new TodoMemento(state); }
    public void restore(TodoMemento m) { this.state = m.getState(); }
}
