package org.example.patterns;
public class FeedSingletonTest {
    public static void main(String[] args) {
        FeedSingleton a = FeedSingleton.getInstance();
        FeedSingleton b = FeedSingleton.getInstance();
        a.setValue("feed-one");
        if (a != b) throw new AssertionError("not singleton");
        if (!b.getValue().equals("feed-one")) throw new AssertionError("state not shared");
        System.out.println("ok");
    }
}
