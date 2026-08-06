package org.example.patterns;
public class ReviewMediatorTest {
    public static void main(String[] args) {
        ReviewMediator m = new ReviewMediator();
        new ReviewColleague("a", m).send("hi");
        if (!m.history().equals("a->hi")) throw new AssertionError();
        System.out.println("ok");
    }
}
