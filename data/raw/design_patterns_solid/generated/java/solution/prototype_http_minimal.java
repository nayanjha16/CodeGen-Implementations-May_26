// DesignPatternsSolid | kind=design_pattern | label=prototype | domain=http | tier=minimal
package org.example.patterns;

public class HttpPrototype implements Cloneable {
    private String label;
    private int weight;

    public HttpPrototype(String label, int weight) {
        this.label = label;
        this.weight = weight;
    }

    public HttpPrototype copy() {
        try {
            return (HttpPrototype) this.clone();
        } catch (CloneNotSupportedException e) {
            throw new RuntimeException(e);
        }
    }

    public void setLabel(String label) { this.label = label; }
    public String describe() { return label + "#" + weight; }
}
