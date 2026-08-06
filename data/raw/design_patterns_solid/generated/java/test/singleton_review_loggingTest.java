package org.example.patterns;
public class ReviewSingletonTest {
    public static void main(String[] args) {
        ReviewSingleton a = ReviewSingleton.getInstance();
        ReviewSingleton b = ReviewSingleton.getInstance();
        a.setValue("review-one");
        if (a != b) throw new AssertionError("not singleton");
        if (!b.getValue().equals("review-one")) throw new AssertionError("state not shared");
        System.out.println("ok");
    }
}
