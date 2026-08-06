// DesignPatternsSolid | kind=design_pattern | label=prototype | domain=plugin | tier=errors
package org.example.patterns;

public class PluginPrototype implements Cloneable {
    private String label;
    private int weight;

    public PluginPrototype(String label, int weight) {
        this.label = label;
        this.weight = weight;
    }

    public PluginPrototype copy() {
        try {
            return (PluginPrototype) this.clone();
        } catch (CloneNotSupportedException e) {
            throw new RuntimeException(e);
        }
    }

    public void setLabel(String label) { this.label = label; }
    public String describe() { return label + "#" + weight; }
}
