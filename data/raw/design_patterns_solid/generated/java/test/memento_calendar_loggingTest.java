package org.example.patterns;
public class CalendarMementoTest {
    public static void main(String[] args) {
        CalendarOriginator o = new CalendarOriginator();
        CalendarMemento m = o.save();
        o.setState("changed");
        o.restore(m);
        if (!o.getState().equals("calendar-init")) throw new AssertionError();
        System.out.println("ok");
    }
}
