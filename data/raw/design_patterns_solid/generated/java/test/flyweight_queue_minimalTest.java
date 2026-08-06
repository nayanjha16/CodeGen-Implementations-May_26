package org.example.patterns;
public class QueueFlyweightTest {
    public static void main(String[] args) {
        QueueFlyweightFactory f = new QueueFlyweightFactory();
        String a = f.intern("a");
        String b = f.intern("a");
        if (a != b) throw new AssertionError();
        if (f.size() != 1) throw new AssertionError();
        System.out.println("ok");
    }
}
