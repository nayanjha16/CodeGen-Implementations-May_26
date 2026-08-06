package org.example.patterns;
public class CommentIspTest {
    public static void main(String[] args) {
        CommentStore st = new CommentStore();
        st.write("x");
        if (!CommentIspClient.mirror(st).equals("comment:x")) throw new AssertionError();
        System.out.println("ok");
    }
}
