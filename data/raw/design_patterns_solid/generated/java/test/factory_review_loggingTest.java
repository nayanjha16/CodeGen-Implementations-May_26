package org.example.patterns;
public class ReviewFactoryTest {
    public static void main(String[] args) {
        ReviewFactory f = new ReviewFactory();
        if (!f.create("basic").operate().equals("basic-review")) throw new AssertionError();
        if (!f.create("premium").operate().equals("premium-review")) throw new AssertionError();
        System.out.println("ok");
    }
}
