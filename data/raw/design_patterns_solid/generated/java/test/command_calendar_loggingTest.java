package org.example.patterns;
public class CalendarCommandTest {
    public static void main(String[] args) {
        CalendarCommand cmd = new CalendarActionCommand(new CalendarReceiver(), "x");
        if (!cmd.execute().equals("done-calendar:x")) throw new AssertionError();
        System.out.println("ok");
    }
}
