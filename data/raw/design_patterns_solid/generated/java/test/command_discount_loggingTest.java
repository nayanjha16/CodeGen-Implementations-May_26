package org.example.patterns;
public class DiscountCommandTest {
    public static void main(String[] args) {
        DiscountCommand cmd = new DiscountActionCommand(new DiscountReceiver(), "x");
        if (!cmd.execute().equals("done-discount:x")) throw new AssertionError();
        System.out.println("ok");
    }
}
