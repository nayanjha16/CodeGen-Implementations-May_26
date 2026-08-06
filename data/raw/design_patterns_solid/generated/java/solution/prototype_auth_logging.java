// DesignPatternsSolid | kind=design_pattern | label=prototype | domain=auth | tier=logging
package org.example.patterns;

public class AuthPrototype implements Cloneable {
    private String label;
    private int weight;

    public AuthPrototype(String label, int weight) {
        this.label = label;
        this.weight = weight;
    }

    public AuthPrototype copy() {
        try {
            return (AuthPrototype) this.clone();
        } catch (CloneNotSupportedException e) {
            throw new RuntimeException(e);
        }
    }

    public void setLabel(String label) { this.label = label; }
    public String describe() { return label + "#" + weight; }
}
