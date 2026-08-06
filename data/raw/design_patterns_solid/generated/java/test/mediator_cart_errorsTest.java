package org.example.patterns;
public class CartMediatorTest {
    public static void main(String[] args) {
        CartMediator m = new CartMediator();
        new CartColleague("a", m).send("hi");
        if (!m.history().equals("a->hi")) throw new AssertionError();
        System.out.println("ok");
    }
}
