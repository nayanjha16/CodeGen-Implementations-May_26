package org.example.patterns;
public class CommentLspTest {
    public static void main(String[] args) {
        CommentShape[] arr = new CommentShape[] { new CommentRectangle(2,3), new CommentSquare(4) };
        if (CommentLspUtil.total(arr) != 22) throw new AssertionError();
        System.out.println("ok");
    }
}
