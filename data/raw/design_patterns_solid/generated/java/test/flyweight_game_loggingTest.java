package org.example.patterns;
public class GameFlyweightTest {
    public static void main(String[] args) {
        GameFlyweightFactory f = new GameFlyweightFactory();
        String a = f.intern("a");
        String b = f.intern("a");
        if (a != b) throw new AssertionError();
        if (f.size() != 1) throw new AssertionError();
        System.out.println("ok");
    }
}
