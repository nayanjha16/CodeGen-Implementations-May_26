package org.example.patterns;
public class CommentFactoryTest {
    public static void main(String[] args) {
        CommentFactory f = new CommentFactory();
        if (!f.create("basic").operate().equals("basic-comment")) throw new AssertionError();
        if (!f.create("premium").operate().equals("premium-comment")) throw new AssertionError();
        System.out.println("ok");
    }
}
