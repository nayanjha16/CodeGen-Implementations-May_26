// DesignPatternsSolid | kind=design_pattern | label=prototype | domain=editor | tier=errors
package org.example.patterns;

public class EditorPrototype implements Cloneable {
    private String label;
    private int weight;

    public EditorPrototype(String label, int weight) {
        this.label = label;
        this.weight = weight;
    }

    public EditorPrototype copy() {
        try {
            return (EditorPrototype) this.clone();
        } catch (CloneNotSupportedException e) {
            throw new RuntimeException(e);
        }
    }

    public void setLabel(String label) { this.label = label; }
    public String describe() { return label + "#" + weight; }
}
