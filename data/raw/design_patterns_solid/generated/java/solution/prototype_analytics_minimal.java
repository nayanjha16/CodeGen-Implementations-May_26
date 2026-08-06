// DesignPatternsSolid | kind=design_pattern | label=prototype | domain=analytics | tier=minimal
package org.example.patterns;

public class AnalyticsPrototype implements Cloneable {
    private String label;
    private int weight;

    public AnalyticsPrototype(String label, int weight) {
        this.label = label;
        this.weight = weight;
    }

    public AnalyticsPrototype copy() {
        try {
            return (AnalyticsPrototype) this.clone();
        } catch (CloneNotSupportedException e) {
            throw new RuntimeException(e);
        }
    }

    public void setLabel(String label) { this.label = label; }
    public String describe() { return label + "#" + weight; }
}
