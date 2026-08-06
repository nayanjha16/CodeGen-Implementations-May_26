package org.example.patterns;
public class CalendarAdapterTest {
    public static void main(String[] args) {
        CalendarTarget t = new CalendarAdapter(new CalendarLegacyApi());
        if (!t.fetch().equals("modern-calendar")) throw new AssertionError(t.fetch());
        System.out.println("ok");
    }
}
