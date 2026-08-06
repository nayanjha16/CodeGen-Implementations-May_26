package org.example.patterns;
public class DiscountMementoTest {
    public static void main(String[] args) {
        DiscountOriginator o = new DiscountOriginator();
        DiscountMemento m = o.save();
        o.setState("changed");
        o.restore(m);
        if (!o.getState().equals("discount-init")) throw new AssertionError();
        System.out.println("ok");
    }
}
