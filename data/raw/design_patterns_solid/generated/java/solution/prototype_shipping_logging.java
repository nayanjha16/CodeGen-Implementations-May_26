// DesignPatternsSolid | kind=design_pattern | label=prototype | domain=shipping | tier=logging
package org.example.patterns;

public class ShippingPrototype implements Cloneable {
    private String label;
    private int weight;

    public ShippingPrototype(String label, int weight) {
        this.label = label;
        this.weight = weight;
    }

    public ShippingPrototype copy() {
        try {
            return (ShippingPrototype) this.clone();
        } catch (CloneNotSupportedException e) {
            throw new RuntimeException(e);
        }
    }

    public void setLabel(String label) { this.label = label; }
    public String describe() { return label + "#" + weight; }
}
