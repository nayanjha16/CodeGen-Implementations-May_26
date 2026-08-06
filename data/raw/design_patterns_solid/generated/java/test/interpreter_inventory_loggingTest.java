package org.example.patterns;
public class InventoryInterpreterTest {
    public static void main(String[] args) {
        InventoryInterpreter i = new InventoryInterpreter();
        if (i.eval("2+3") != 5) throw new AssertionError();
        System.out.println("ok");
    }
}
