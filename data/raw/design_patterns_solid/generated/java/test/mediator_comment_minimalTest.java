package org.example.patterns;
public class CommentMediatorTest {
    public static void main(String[] args) {
        CommentMediator m = new CommentMediator();
        new CommentColleague("a", m).send("hi");
        if (!m.history().equals("a->hi")) throw new AssertionError();
        System.out.println("ok");
    }
}
