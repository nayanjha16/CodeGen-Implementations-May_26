package org.example.patterns;
public class FeedMediatorTest {
    public static void main(String[] args) {
        FeedMediator m = new FeedMediator();
        new FeedColleague("a", m).send("hi");
        if (!m.history().equals("a->hi")) throw new AssertionError();
        System.out.println("ok");
    }
}
