package org.example.patterns;
public class CalendarMediatorTest {
    public static void main(String[] args) {
        CalendarMediator m = new CalendarMediator();
        new CalendarColleague("a", m).send("hi");
        if (!m.history().equals("a->hi")) throw new AssertionError();
        System.out.println("ok");
    }
}
