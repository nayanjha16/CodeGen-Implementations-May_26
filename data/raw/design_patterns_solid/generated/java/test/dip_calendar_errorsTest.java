package org.example.patterns;
public class CalendarDipTest {
    public static void main(String[] args) {
        String out = new CalendarAppService(new CalendarHttpGateway()).publish("p");
        if (!out.equals("http-calendar:p")) throw new AssertionError(out);
        System.out.println("ok");
    }
}
