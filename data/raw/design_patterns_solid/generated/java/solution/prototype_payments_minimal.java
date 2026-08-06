// DesignPatternsSolid | kind=design_pattern | label=prototype | domain=payments | tier=minimal
package org.example.patterns;

public class PaymentsPrototype implements Cloneable {
    private String label;
    private int weight;

    public PaymentsPrototype(String label, int weight) {
        this.label = label;
        this.weight = weight;
    }

    public PaymentsPrototype copy() {
        try {
            return (PaymentsPrototype) this.clone();
        } catch (CloneNotSupportedException e) {
            throw new RuntimeException(e);
        }
    }

    public void setLabel(String label) { this.label = label; }
    public String describe() { return label + "#" + weight; }
}
