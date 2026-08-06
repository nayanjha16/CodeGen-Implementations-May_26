package org.example.patterns;
public class InventoryFactoryTest {
    public static void main(String[] args) {
        InventoryFactory f = new InventoryFactory();
        if (!f.create("basic").operate().equals("basic-inventory")) throw new AssertionError();
        if (!f.create("premium").operate().equals("premium-inventory")) throw new AssertionError();
        System.out.println("ok");
    }
}
