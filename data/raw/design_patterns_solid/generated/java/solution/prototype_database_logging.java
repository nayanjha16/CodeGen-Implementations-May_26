// DesignPatternsSolid | kind=design_pattern | label=prototype | domain=database | tier=logging
package org.example.patterns;

public class DatabasePrototype implements Cloneable {
    private String label;
    private int weight;

    public DatabasePrototype(String label, int weight) {
        this.label = label;
        this.weight = weight;
    }

    public DatabasePrototype copy() {
        try {
            return (DatabasePrototype) this.clone();
        } catch (CloneNotSupportedException e) {
            throw new RuntimeException(e);
        }
    }

    public void setLabel(String label) { this.label = label; }
    public String describe() { return label + "#" + weight; }
}
