package org.example.patterns;
public class ShippingCommandTest {
    public static void main(String[] args) {
        ShippingCommand cmd = new ShippingActionCommand(new ShippingReceiver(), "x");
        if (!cmd.execute().equals("done-shipping:x")) throw new AssertionError();
        System.out.println("ok");
    }
}
