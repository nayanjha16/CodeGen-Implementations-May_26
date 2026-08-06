package org.example.patterns;
public class CartObserverTest {
    public static void main(String[] args) {
        CartSubject s = new CartSubject();
        CartListener l = new CartListener();
        s.attach(l);
        s.notifyAllObservers("e");
        if (!l.last.equals("cart:e")) throw new AssertionError();
        System.out.println("ok");
    }
}
