// DesignPatternsSolid | kind=design_pattern | label=prototype | domain=calendar | tier=minimal
package org.example.patterns;

public class CalendarPrototype implements Cloneable {
    private String label;
    private int weight;

    public CalendarPrototype(String label, int weight) {
        this.label = label;
        this.weight = weight;
    }

    public CalendarPrototype copy() {
        try {
            return (CalendarPrototype) this.clone();
        } catch (CloneNotSupportedException e) {
            throw new RuntimeException(e);
        }
    }

    public void setLabel(String label) { this.label = label; }
    public String describe() { return label + "#" + weight; }
}
