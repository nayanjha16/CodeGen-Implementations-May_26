// DesignPatternsSolid | kind=combo | label=decorator+ocp | domain=inventory | tier=minimal
package org.example.patterns;

interface InventoryComponent {
    String process(String input);
}

class InventoryCore implements InventoryComponent {
    public String process(String input) { return "inventory:" + input; }
}

public class InventoryUpperDecorator implements InventoryComponent {
    private final InventoryComponent inner;
    public InventoryUpperDecorator(InventoryComponent inner) { this.inner = inner; }
    public String process(String input) {
        return inner.process(input).toUpperCase();
    }
}
