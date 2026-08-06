// DesignPatternsSolid | kind=design_pattern | label=prototype | domain=chat | tier=logging
package org.example.patterns;

public class ChatPrototype implements Cloneable {
    private String label;
    private int weight;

    public ChatPrototype(String label, int weight) {
        this.label = label;
        this.weight = weight;
    }

    public ChatPrototype copy() {
        try {
            return (ChatPrototype) this.clone();
        } catch (CloneNotSupportedException e) {
            throw new RuntimeException(e);
        }
    }

    public void setLabel(String label) { this.label = label; }
    public String describe() { return label + "#" + weight; }
}
