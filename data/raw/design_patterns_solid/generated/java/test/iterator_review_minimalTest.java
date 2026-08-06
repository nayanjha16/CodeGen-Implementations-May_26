package org.example.patterns;
public class ReviewIteratorTest {
    public static void main(String[] args) {
        ReviewCollection col = new ReviewCollection();
        col.add("a"); col.add("b");
        if (!col.join().equals("review:a:b")) throw new AssertionError(col.join());
        System.out.println("ok");
    }
}
