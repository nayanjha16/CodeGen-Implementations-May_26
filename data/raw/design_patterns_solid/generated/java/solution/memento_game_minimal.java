// DesignPatternsSolid | kind=design_pattern | label=memento | domain=game | tier=minimal
package org.example.patterns;

public class GameMemento {
    private final String state;
    public GameMemento(String state) { this.state = state; }
    public String getState() { return state; }
}

class GameOriginator {
    private String state = "game-init";
    public void setState(String state) { this.state = state; }
    public String getState() { return state; }
    public GameMemento save() { return new GameMemento(state); }
    public void restore(GameMemento m) { this.state = m.getState(); }
}
