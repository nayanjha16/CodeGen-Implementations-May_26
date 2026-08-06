package org.example.patterns;
public class FeedIteratorTest {
    public static void main(String[] args) {
        FeedCollection col = new FeedCollection();
        col.add("a"); col.add("b");
        if (!col.join().equals("feed:a:b")) throw new AssertionError(col.join());
        System.out.println("ok");
    }
}
