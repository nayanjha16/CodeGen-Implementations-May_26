package org.example.patterns;
public class CalendarIspTest {
    public static void main(String[] args) {
        CalendarStore st = new CalendarStore();
        st.write("x");
        if (!CalendarIspClient.mirror(st).equals("calendar:x")) throw new AssertionError();
        System.out.println("ok");
    }
}
