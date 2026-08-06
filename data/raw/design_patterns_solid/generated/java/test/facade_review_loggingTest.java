package org.example.patterns;
public class ReviewFacadeTest {
    public static void main(String[] args) {
        ReviewFacade f = new ReviewFacade();
        if (!f.submit("x").equals("wrote-review:x")) throw new AssertionError();
        System.out.println("ok");
    }
}
