package org.example.patterns;
public class SmsCommandTest {
    public static void main(String[] args) {
        SmsCommand cmd = new SmsActionCommand(new SmsReceiver(), "x");
        if (!cmd.execute().equals("done-sms:x")) throw new AssertionError();
        System.out.println("ok");
    }
}
