package org.example.patterns;
public class InventoryBuilderTest {
    public static void main(String[] args) {
        InventoryConfig cfg = new InventoryConfig.Builder().name("inventory-x").limit(3).enabled(false).build();
        if (!cfg.summary().equals("inventory-x:3:false")) throw new AssertionError(cfg.summary());
        System.out.println("ok");
    }
}
