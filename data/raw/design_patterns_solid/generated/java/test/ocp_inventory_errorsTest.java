package org.example.patterns;
public class InventoryOcpTest {
    public static void main(String[] args) {
        if (new InventoryPriceEngine(new InventoryTenPercent()).quote(100) != 90) throw new AssertionError();
        System.out.println("ok");
    }
}
