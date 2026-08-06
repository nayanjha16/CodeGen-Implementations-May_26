package org.example.patterns;
public class InventoryTemplateTest {
    public static void main(String[] args) {
        String out = new InventoryUpperTemplate().run(" ab ");
        if (!out.equals("inventory|AB")) throw new AssertionError(out);
        System.out.println("ok");
    }
}
