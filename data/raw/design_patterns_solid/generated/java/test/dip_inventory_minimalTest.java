package org.example.patterns;
public class InventoryDipTest {
    public static void main(String[] args) {
        String out = new InventoryAppService(new InventoryHttpGateway()).publish("p");
        if (!out.equals("http-inventory:p")) throw new AssertionError(out);
        System.out.println("ok");
    }
}
