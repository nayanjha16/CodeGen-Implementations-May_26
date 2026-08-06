// DesignPatternsSolid | kind=design_pattern | label=prototype | domain=license | tier=logging
package org.example.patterns;

public class LicensePrototype implements Cloneable {
    private String label;
    private int weight;

    public LicensePrototype(String label, int weight) {
        this.label = label;
        this.weight = weight;
    }

    public LicensePrototype copy() {
        try {
            return (LicensePrototype) this.clone();
        } catch (CloneNotSupportedException e) {
            throw new RuntimeException(e);
        }
    }

    public void setLabel(String label) { this.label = label; }
    public String describe() { return label + "#" + weight; }
}
