// DesignPatternsSolid | kind=design_pattern | label=prototype | domain=map | tier=logging
package org.example.patterns;

public class MapPrototype implements Cloneable {
    private String label;
    private int weight;

    public MapPrototype(String label, int weight) {
        this.label = label;
        this.weight = weight;
    }

    public MapPrototype copy() {
        try {
            return (MapPrototype) this.clone();
        } catch (CloneNotSupportedException e) {
            throw new RuntimeException(e);
        }
    }

    public void setLabel(String label) { this.label = label; }
    public String describe() { return label + "#" + weight; }
}
