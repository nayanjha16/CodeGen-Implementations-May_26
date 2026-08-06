package org.example.patterns;
public class FeedFactoryTest {
    public static void main(String[] args) {
        FeedFactory f = new FeedFactory();
        if (!f.create("basic").operate().equals("basic-feed")) throw new AssertionError();
        if (!f.create("premium").operate().equals("premium-feed")) throw new AssertionError();
        System.out.println("ok");
    }
}
