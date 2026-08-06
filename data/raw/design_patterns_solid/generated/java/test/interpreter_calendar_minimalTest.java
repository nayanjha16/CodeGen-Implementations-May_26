package org.example.patterns;
public class CalendarInterpreterTest {
    public static void main(String[] args) {
        CalendarInterpreter i = new CalendarInterpreter();
        if (i.eval("2+3") != 5) throw new AssertionError();
        System.out.println("ok");
    }
}
