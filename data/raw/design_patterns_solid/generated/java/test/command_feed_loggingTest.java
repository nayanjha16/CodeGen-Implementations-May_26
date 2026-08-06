package org.example.patterns;
public class FeedCommandTest {
    public static void main(String[] args) {
        FeedCommand cmd = new FeedActionCommand(new FeedReceiver(), "x");
        if (!cmd.execute().equals("done-feed:x")) throw new AssertionError();
        System.out.println("ok");
    }
}
