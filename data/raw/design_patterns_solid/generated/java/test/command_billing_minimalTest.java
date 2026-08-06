package org.example.patterns;
public class BillingCommandTest {
    public static void main(String[] args) {
        BillingCommand cmd = new BillingActionCommand(new BillingReceiver(), "x");
        if (!cmd.execute().equals("done-billing:x")) throw new AssertionError();
        System.out.println("ok");
    }
}
