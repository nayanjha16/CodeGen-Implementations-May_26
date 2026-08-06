package org.example.patterns;
public class FeedPrototypeTest {
    public static void main(String[] args) {
        FeedPrototype a = new FeedPrototype("feed", 2);
        FeedPrototype b = a.copy();
        b.setLabel("feed-copy");
        if (a.describe().equals(b.describe())) throw new AssertionError();
        System.out.println("ok");
    }
}
