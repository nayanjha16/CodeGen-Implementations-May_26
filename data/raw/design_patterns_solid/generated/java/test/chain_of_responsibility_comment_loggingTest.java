package org.example.patterns;
public class CommentChainTest {
    public static void main(String[] args) {
        CommentHandler h = new CommentLowHandler();
        h.link(new CommentHighHandler());
        if (!h.handle(2, "m").equals("high-comment:m")) throw new AssertionError();
        System.out.println("ok");
    }
}
