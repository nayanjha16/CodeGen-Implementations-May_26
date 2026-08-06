package org.example.patterns;
public class WidgetsMediatorTest {
    public static void main(String[] args) {
        WidgetsMediator m = new WidgetsMediator();
        new WidgetsColleague("a", m).send("hi");
        if (!m.history().equals("a->hi")) throw new AssertionError();
        System.out.println("ok");
    }
}
