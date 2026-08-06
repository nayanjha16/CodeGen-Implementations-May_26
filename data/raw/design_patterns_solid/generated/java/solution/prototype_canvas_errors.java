// DesignPatternsSolid | kind=design_pattern | label=prototype | domain=canvas | tier=errors
package org.example.patterns;

public class CanvasPrototype implements Cloneable {
    private String label;
    private int weight;

    public CanvasPrototype(String label, int weight) {
        this.label = label;
        this.weight = weight;
    }

    public CanvasPrototype copy() {
        try {
            return (CanvasPrototype) this.clone();
        } catch (CloneNotSupportedException e) {
            throw new RuntimeException(e);
        }
    }

    public void setLabel(String label) { this.label = label; }
    public String describe() { return label + "#" + weight; }
}
