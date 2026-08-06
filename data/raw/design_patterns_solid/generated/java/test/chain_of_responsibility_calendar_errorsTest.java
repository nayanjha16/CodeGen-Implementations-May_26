package org.example.patterns;
public class CalendarChainTest {
    public static void main(String[] args) {
        CalendarHandler h = new CalendarLowHandler();
        h.link(new CalendarHighHandler());
        if (!h.handle(2, "m").equals("high-calendar:m")) throw new AssertionError();
        System.out.println("ok");
    }
}
