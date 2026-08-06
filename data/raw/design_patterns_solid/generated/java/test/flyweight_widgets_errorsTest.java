package org.example.patterns;
public class WidgetsFlyweightTest {
    public static void main(String[] args) {
        WidgetsFlyweightFactory f = new WidgetsFlyweightFactory();
        String a = f.intern("a");
        String b = f.intern("a");
        if (a != b) throw new AssertionError();
        if (f.size() != 1) throw new AssertionError();
        System.out.println("ok");
    }
}
