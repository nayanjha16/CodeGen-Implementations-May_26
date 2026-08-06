package org.example.patterns;
public class CommentPrototypeTest {
    public static void main(String[] args) {
        CommentPrototype a = new CommentPrototype("comment", 2);
        CommentPrototype b = a.copy();
        b.setLabel("comment-copy");
        if (a.describe().equals(b.describe())) throw new AssertionError();
        System.out.println("ok");
    }
}
