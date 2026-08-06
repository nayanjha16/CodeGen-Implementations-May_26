package org.example.patterns;
public class FeedChainTest {
    public static void main(String[] args) {
        FeedHandler h = new FeedLowHandler();
        h.link(new FeedHighHandler());
        if (!h.handle(2, "m").equals("high-feed:m")) throw new AssertionError();
        System.out.println("ok");
    }
}
