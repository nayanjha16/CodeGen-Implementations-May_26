package org.example.patterns;
public class InventoryBridgeTest {
    public static void main(String[] args) {
        InventoryBridge b = new InventoryAlertBridge(new InventoryFileImpl());
        String out = b.send("x");
        if (!out.equals("file:inventory:ALERT-x")) throw new AssertionError(out);
        System.out.println("ok");
    }
}
