package org.example.patterns;
public class CommentAdapterTest {
    public static void main(String[] args) {
        CommentTarget t = new CommentAdapter(new CommentLegacyApi());
        if (!t.fetch().equals("modern-comment")) throw new AssertionError(t.fetch());
        System.out.println("ok");
    }
}
