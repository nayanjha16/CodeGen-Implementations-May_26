package org.example.patterns;
public class EmailCommandTest {
    public static void main(String[] args) {
        EmailCommand cmd = new EmailActionCommand(new EmailReceiver(), "x");
        if (!cmd.execute().equals("done-email:x")) throw new AssertionError();
        System.out.println("ok");
    }
}
