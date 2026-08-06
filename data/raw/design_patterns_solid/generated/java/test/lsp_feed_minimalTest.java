package org.example.patterns;
public class FeedLspTest {
    public static void main(String[] args) {
        FeedShape[] arr = new FeedShape[] { new FeedRectangle(2,3), new FeedSquare(4) };
        if (FeedLspUtil.total(arr) != 22) throw new AssertionError();
        System.out.println("ok");
    }
}
