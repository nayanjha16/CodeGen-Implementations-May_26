// DesignPatternsSolid | kind=design_pattern | label=prototype | domain=streaming | tier=minimal
package org.example.patterns;

public class StreamingPrototype implements Cloneable {
    private String label;
    private int weight;

    public StreamingPrototype(String label, int weight) {
        this.label = label;
        this.weight = weight;
    }

    public StreamingPrototype copy() {
        try {
            return (StreamingPrototype) this.clone();
        } catch (CloneNotSupportedException e) {
            throw new RuntimeException(e);
        }
    }

    public void setLabel(String label) { this.label = label; }
    public String describe() { return label + "#" + weight; }
}
