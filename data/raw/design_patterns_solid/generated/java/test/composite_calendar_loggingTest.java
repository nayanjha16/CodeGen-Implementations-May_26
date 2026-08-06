package org.example.patterns;
public class CalendarCompositeTest {
    public static void main(String[] args) {
        CalendarComposite root = new CalendarComposite();
        root.add(new CalendarLeaf(2));
        root.add(new CalendarLeaf(3));
        if (root.size() != 5) throw new AssertionError();
        System.out.println("ok");
    }
}
