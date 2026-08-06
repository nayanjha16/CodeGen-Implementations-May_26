// DesignPatternsSolid | kind=design_pattern | label=prototype | domain=search | tier=errors
package org.example.patterns;

public class SearchPrototype implements Cloneable {
    private String label;
    private int weight;

    public SearchPrototype(String label, int weight) {
        this.label = label;
        this.weight = weight;
    }

    public SearchPrototype copy() {
        try {
            return (SearchPrototype) this.clone();
        } catch (CloneNotSupportedException e) {
            throw new RuntimeException(e);
        }
    }

    public void setLabel(String label) { this.label = label; }
    public String describe() { return label + "#" + weight; }
}
