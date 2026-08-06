// DesignPatternsSolid | kind=design_pattern | label=prototype | domain=sms | tier=minimal
package org.example.patterns;

public class SmsPrototype implements Cloneable {
    private String label;
    private int weight;

    public SmsPrototype(String label, int weight) {
        this.label = label;
        this.weight = weight;
    }

    public SmsPrototype copy() {
        try {
            return (SmsPrototype) this.clone();
        } catch (CloneNotSupportedException e) {
            throw new RuntimeException(e);
        }
    }

    public void setLabel(String label) { this.label = label; }
    public String describe() { return label + "#" + weight; }
}
