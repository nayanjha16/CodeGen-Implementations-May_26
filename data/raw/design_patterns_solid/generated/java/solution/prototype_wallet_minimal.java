// DesignPatternsSolid | kind=design_pattern | label=prototype | domain=wallet | tier=minimal
package org.example.patterns;

public class WalletPrototype implements Cloneable {
    private String label;
    private int weight;

    public WalletPrototype(String label, int weight) {
        this.label = label;
        this.weight = weight;
    }

    public WalletPrototype copy() {
        try {
            return (WalletPrototype) this.clone();
        } catch (CloneNotSupportedException e) {
            throw new RuntimeException(e);
        }
    }

    public void setLabel(String label) { this.label = label; }
    public String describe() { return label + "#" + weight; }
}
