package org.example.patterns;
public class CommentFacadeTest {
    public static void main(String[] args) {
        CommentFacade f = new CommentFacade();
        if (!f.submit("x").equals("wrote-comment:x")) throw new AssertionError();
        System.out.println("ok");
    }
}
