package org.example.patterns;
public class WidgetsSingletonTest {
    public static void main(String[] args) {
        WidgetsSingleton a = WidgetsSingleton.getInstance();
        WidgetsSingleton b = WidgetsSingleton.getInstance();
        a.setValue("widgets-one");
        if (a != b) throw new AssertionError("not singleton");
        if (!b.getValue().equals("widgets-one")) throw new AssertionError("state not shared");
        System.out.println("ok");
    }
}
