package org.example.patterns;
public class ReviewIspTest {
    public static void main(String[] args) {
        ReviewStore st = new ReviewStore();
        st.write("x");
        if (!ReviewIspClient.mirror(st).equals("review:x")) throw new AssertionError();
        System.out.println("ok");
    }
}
