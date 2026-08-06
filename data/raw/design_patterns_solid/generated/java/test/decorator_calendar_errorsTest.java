package org.example.patterns;
public class CalendarDecoratorTest {
    public static void main(String[] args) {
        CalendarComponent c = new CalendarUpperDecorator(new CalendarCore());
        String out = c.process("ab");
        if (!out.equals("CALENDAR:AB")) throw new AssertionError(out);
        System.out.println("ok");
    }
}
