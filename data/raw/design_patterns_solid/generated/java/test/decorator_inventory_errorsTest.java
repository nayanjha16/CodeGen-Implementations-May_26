package org.example.patterns;
public class InventoryDecoratorTest {
    public static void main(String[] args) {
        InventoryComponent c = new InventoryUpperDecorator(new InventoryCore());
        String out = c.process("ab");
        if (!out.equals("INVENTORY:AB")) throw new AssertionError(out);
        System.out.println("ok");
    }
}
