package org.example.patterns;
public class TicketCommandTest {
    public static void main(String[] args) {
        TicketCommand cmd = new TicketActionCommand(new TicketReceiver(), "x");
        if (!cmd.execute().equals("done-ticket:x")) throw new AssertionError();
        System.out.println("ok");
    }
}
