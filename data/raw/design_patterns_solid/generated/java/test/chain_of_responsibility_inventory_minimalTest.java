package org.example.patterns;
public class InventoryChainTest {
    public static void main(String[] args) {
        InventoryHandler h = new InventoryLowHandler();
        h.link(new InventoryHighHandler());
        if (!h.handle(2, "m").equals("high-inventory:m")) throw new AssertionError();
        System.out.println("ok");
    }
}
