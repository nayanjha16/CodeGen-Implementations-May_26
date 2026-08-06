package org.example.patterns;
public class InventoryObserverTest {
    public static void main(String[] args) {
        InventorySubject s = new InventorySubject();
        InventoryListener l = new InventoryListener();
        s.attach(l);
        s.notifyAllObservers("e");
        if (!l.last.equals("inventory:e")) throw new AssertionError();
        System.out.println("ok");
    }
}
