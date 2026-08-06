package org.example.patterns;
public class InventorySrpTest {
    public static void main(String[] args) {
        InventoryRecord r = new InventoryRecord("a", 3);
        if (!new InventoryFormatter().format(r).equals("a=3")) throw new AssertionError();
        System.out.println("ok");
    }
}
