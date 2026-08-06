// DesignPatternsSolid | kind=design_pattern | label=prototype | domain=metrics | tier=errors
package org.example.patterns;

public class MetricsPrototype implements Cloneable {
    private String label;
    private int weight;

    public MetricsPrototype(String label, int weight) {
        this.label = label;
        this.weight = weight;
    }

    public MetricsPrototype copy() {
        try {
            return (MetricsPrototype) this.clone();
        } catch (CloneNotSupportedException e) {
            throw new RuntimeException(e);
        }
    }

    public void setLabel(String label) { this.label = label; }
    public String describe() { return label + "#" + weight; }
}
