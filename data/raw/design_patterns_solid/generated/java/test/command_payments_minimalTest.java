package org.example.patterns;
public class PaymentsCommandTest {
    public static void main(String[] args) {
        PaymentsCommand cmd = new PaymentsActionCommand(new PaymentsReceiver(), "x");
        if (!cmd.execute().equals("done-payments:x")) throw new AssertionError();
        System.out.println("ok");
    }
}
