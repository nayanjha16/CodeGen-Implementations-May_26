// DesignPatternsSolid | kind=design_pattern | label=prototype | domain=logging | tier=minimal
package org.example.patterns;

public class LoggingPrototype implements Cloneable {
    private String label;
    private int weight;

    public LoggingPrototype(String label, int weight) {
        this.label = label;
        this.weight = weight;
    }

    public LoggingPrototype copy() {
        try {
            return (LoggingPrototype) this.clone();
        } catch (CloneNotSupportedException e) {
            throw new RuntimeException(e);
        }
    }

    public void setLabel(String label) { this.label = label; }
    public String describe() { return label + "#" + weight; }
}
