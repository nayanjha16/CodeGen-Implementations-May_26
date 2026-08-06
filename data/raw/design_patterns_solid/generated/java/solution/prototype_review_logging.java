// DesignPatternsSolid | kind=design_pattern | label=prototype | domain=review | tier=logging
package org.example.patterns;

public class ReviewPrototype implements Cloneable {
    private String label;
    private int weight;

    public ReviewPrototype(String label, int weight) {
        this.label = label;
        this.weight = weight;
    }

    public ReviewPrototype copy() {
        try {
            return (ReviewPrototype) this.clone();
        } catch (CloneNotSupportedException e) {
            throw new RuntimeException(e);
        }
    }

    public void setLabel(String label) { this.label = label; }
    public String describe() { return label + "#" + weight; }
}
