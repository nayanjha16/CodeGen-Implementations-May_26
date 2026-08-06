package org.example.patterns;
public class CartMementoTest {
    public static void main(String[] args) {
        CartOriginator o = new CartOriginator();
        CartMemento m = o.save();
        o.setState("changed");
        o.restore(m);
        if (!o.getState().equals("cart-init")) throw new AssertionError();
        System.out.println("ok");
    }
}
