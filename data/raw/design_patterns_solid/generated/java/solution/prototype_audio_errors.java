// DesignPatternsSolid | kind=design_pattern | label=prototype | domain=audio | tier=errors
package org.example.patterns;

public class AudioPrototype implements Cloneable {
    private String label;
    private int weight;

    public AudioPrototype(String label, int weight) {
        this.label = label;
        this.weight = weight;
    }

    public AudioPrototype copy() {
        try {
            return (AudioPrototype) this.clone();
        } catch (CloneNotSupportedException e) {
            throw new RuntimeException(e);
        }
    }

    public void setLabel(String label) { this.label = label; }
    public String describe() { return label + "#" + weight; }
}
