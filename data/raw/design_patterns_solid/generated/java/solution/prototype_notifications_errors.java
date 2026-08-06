// DesignPatternsSolid | kind=design_pattern | label=prototype | domain=notifications | tier=errors
package org.example.patterns;

public class NotificationsPrototype implements Cloneable {
    private String label;
    private int weight;

    public NotificationsPrototype(String label, int weight) {
        this.label = label;
        this.weight = weight;
    }

    public NotificationsPrototype copy() {
        try {
            return (NotificationsPrototype) this.clone();
        } catch (CloneNotSupportedException e) {
            throw new RuntimeException(e);
        }
    }

    public void setLabel(String label) { this.label = label; }
    public String describe() { return label + "#" + weight; }
}
