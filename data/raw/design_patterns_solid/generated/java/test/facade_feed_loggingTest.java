package org.example.patterns;
public class FeedFacadeTest {
    public static void main(String[] args) {
        FeedFacade f = new FeedFacade();
        if (!f.submit("x").equals("wrote-feed:x")) throw new AssertionError();
        System.out.println("ok");
    }
}
