package org.example.patterns;
public class ReviewStateTest {
    public static void main(String[] args) {
        ReviewContext ctx = new ReviewContext();
        if (!ctx.request().equals("was-off-review")) throw new AssertionError();
        if (!ctx.request().equals("was-on-review")) throw new AssertionError();
        System.out.println("ok");
    }
}
