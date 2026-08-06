// DesignPatternsSolid | kind=design_pattern | label=prototype | domain=feed | tier=logging
package org.example.patterns;

public class FeedPrototype implements Cloneable {
    private String label;
    private int weight;

    public FeedPrototype(String label, int weight) {
        this.label = label;
        this.weight = weight;
    }

    public FeedPrototype copy() {
        try {
            return (FeedPrototype) this.clone();
        } catch (CloneNotSupportedException e) {
            throw new RuntimeException(e);
        }
    }

    public void setLabel(String label) { this.label = label; }
    public String describe() { return label + "#" + weight; }
}
