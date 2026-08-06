package org.example.patterns;
public class FeedSrpTest {
    public static void main(String[] args) {
        FeedRecord r = new FeedRecord("a", 3);
        if (!new FeedFormatter().format(r).equals("a=3")) throw new AssertionError();
        System.out.println("ok");
    }
}
