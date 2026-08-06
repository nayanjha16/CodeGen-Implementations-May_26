package org.example.patterns;
public class InventoryStateTest {
    public static void main(String[] args) {
        InventoryContext ctx = new InventoryContext();
        if (!ctx.request().equals("was-off-inventory")) throw new AssertionError();
        if (!ctx.request().equals("was-on-inventory")) throw new AssertionError();
        System.out.println("ok");
    }
}
