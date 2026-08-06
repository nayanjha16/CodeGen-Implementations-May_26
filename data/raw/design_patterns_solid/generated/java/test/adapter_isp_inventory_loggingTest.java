package org.example.patterns;
public class InventoryAdapterTest {
    public static void main(String[] args) {
        InventoryTarget t = new InventoryAdapter(new InventoryLegacyApi());
        if (!t.fetch().equals("modern-inventory")) throw new AssertionError(t.fetch());
        System.out.println("ok");
    }
}
