package org.example.patterns;
public class CalendarSingletonTest {
    public static void main(String[] args) {
        CalendarSingleton a = CalendarSingleton.getInstance();
        CalendarSingleton b = CalendarSingleton.getInstance();
        a.setValue("calendar-one");
        if (a != b) throw new AssertionError("not singleton");
        if (!b.getValue().equals("calendar-one")) throw new AssertionError("state not shared");
        System.out.println("ok");
    }
}
