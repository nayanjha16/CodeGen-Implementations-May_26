// DesignPatternsSolid | kind=design_pattern | label=prototype | domain=game | tier=minimal
package org.example.patterns;

public class GamePrototype implements Cloneable {
    private String label;
    private int weight;

    public GamePrototype(String label, int weight) {
        this.label = label;
        this.weight = weight;
    }

    public GamePrototype copy() {
        try {
            return (GamePrototype) this.clone();
        } catch (CloneNotSupportedException e) {
            throw new RuntimeException(e);
        }
    }

    public void setLabel(String label) { this.label = label; }
    public String describe() { return label + "#" + weight; }
}
