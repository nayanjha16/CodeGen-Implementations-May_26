package org.example.patterns;
public class DiscountFacadeTest {
    public static void main(String[] args) {
        DiscountFacade f = new DiscountFacade();
        if (!f.submit("x").equals("wrote-discount:x")) throw new AssertionError();
        System.out.println("ok");
    }
}
