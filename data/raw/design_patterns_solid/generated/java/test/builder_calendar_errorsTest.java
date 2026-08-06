package org.example.patterns;
public class CalendarBuilderTest {
    public static void main(String[] args) {
        CalendarConfig cfg = new CalendarConfig.Builder().name("calendar-x").limit(3).enabled(false).build();
        if (!cfg.summary().equals("calendar-x:3:false")) throw new AssertionError(cfg.summary());
        System.out.println("ok");
    }
}
