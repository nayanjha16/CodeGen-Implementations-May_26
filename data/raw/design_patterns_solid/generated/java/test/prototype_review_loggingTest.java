package org.example.patterns;
public class ReviewPrototypeTest {
    public static void main(String[] args) {
        ReviewPrototype a = new ReviewPrototype("review", 2);
        ReviewPrototype b = a.copy();
        b.setLabel("review-copy");
        if (a.describe().equals(b.describe())) throw new AssertionError();
        System.out.println("ok");
    }
}
