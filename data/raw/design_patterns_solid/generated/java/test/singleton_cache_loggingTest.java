package org.example.patterns;
public class CacheSingletonTest {
    public static void main(String[] args) {
        CacheSingleton a = CacheSingleton.getInstance();
        CacheSingleton b = CacheSingleton.getInstance();
        a.setValue("cache-one");
        if (a != b) throw new AssertionError("not singleton");
        if (!b.getValue().equals("cache-one")) throw new AssertionError("state not shared");
        System.out.println("ok");
    }
}
