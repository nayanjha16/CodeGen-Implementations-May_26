package org.example.patterns;
public class BookingCommandTest {
    public static void main(String[] args) {
        BookingCommand cmd = new BookingActionCommand(new BookingReceiver(), "x");
        if (!cmd.execute().equals("done-booking:x")) throw new AssertionError();
        System.out.println("ok");
    }
}
