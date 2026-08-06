package org.example.patterns;
public class CalendarPrototypeTest {
    public static void main(String[] args) {
        CalendarPrototype a = new CalendarPrototype("calendar", 2);
        CalendarPrototype b = a.copy();
        b.setLabel("calendar-copy");
        if (a.describe().equals(b.describe())) throw new AssertionError();
        System.out.println("ok");
    }
}
