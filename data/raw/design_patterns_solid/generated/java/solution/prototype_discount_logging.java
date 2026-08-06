// DesignPatternsSolid | kind=design_pattern | label=prototype | domain=discount | tier=logging
package org.example.patterns;

public class DiscountPrototype implements Cloneable {
    private String label;
    private int weight;

    public DiscountPrototype(String label, int weight) {
        this.label = label;
        this.weight = weight;
    }

    public DiscountPrototype copy() {
        try {
            return (DiscountPrototype) this.clone();
        } catch (CloneNotSupportedException e) {
            throw new RuntimeException(e);
        }
    }

    public void setLabel(String label) { this.label = label; }
    public String describe() { return label + "#" + weight; }
}
