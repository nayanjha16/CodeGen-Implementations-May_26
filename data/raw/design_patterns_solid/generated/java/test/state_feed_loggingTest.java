package org.example.patterns;
public class FeedStateTest {
    public static void main(String[] args) {
        FeedContext ctx = new FeedContext();
        if (!ctx.request().equals("was-off-feed")) throw new AssertionError();
        if (!ctx.request().equals("was-on-feed")) throw new AssertionError();
        System.out.println("ok");
    }
}
