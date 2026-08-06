// DesignPatternsSolid | kind=design_pattern | label=prototype | domain=cart | tier=minimal
package org.example.patterns;

public class CartPrototype implements Cloneable {
    private String label;
    private int weight;

    public CartPrototype(String label, int weight) {
        this.label = label;
        this.weight = weight;
    }

    public CartPrototype copy() {
        try {
            return (CartPrototype) this.clone();
        } catch (CloneNotSupportedException e) {
            throw new RuntimeException(e);
        }
    }

    public void setLabel(String label) { this.label = label; }
    public String describe() { return label + "#" + weight; }
}
