package org.example.patterns;
public class InventorySingletonTest {
    public static void main(String[] args) {
        InventorySingleton a = InventorySingleton.getInstance();
        InventorySingleton b = InventorySingleton.getInstance();
        a.setValue("inventory-one");
        if (a != b) throw new AssertionError("not singleton");
        if (!b.getValue().equals("inventory-one")) throw new AssertionError("state not shared");
        System.out.println("ok");
    }
}
