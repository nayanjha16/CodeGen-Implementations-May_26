// DesignPatternsSolid | kind=design_pattern | label=prototype | domain=todo | tier=errors
package org.example.patterns;

public class TodoPrototype implements Cloneable {
    private String label;
    private int weight;

    public TodoPrototype(String label, int weight) {
        this.label = label;
        this.weight = weight;
    }

    public TodoPrototype copy() {
        try {
            return (TodoPrototype) this.clone();
        } catch (CloneNotSupportedException e) {
            throw new RuntimeException(e);
        }
    }

    public void setLabel(String label) { this.label = label; }
    public String describe() { return label + "#" + weight; }
}
