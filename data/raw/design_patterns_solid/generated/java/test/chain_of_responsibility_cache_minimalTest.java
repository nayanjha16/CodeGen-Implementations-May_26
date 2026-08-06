package org.example.patterns;
public class CacheChainTest {
    public static void main(String[] args) {
        CacheHandler h = new CacheLowHandler();
        h.link(new CacheHighHandler());
        if (!h.handle(2, "m").equals("high-cache:m")) throw new AssertionError();
        System.out.println("ok");
    }
}
