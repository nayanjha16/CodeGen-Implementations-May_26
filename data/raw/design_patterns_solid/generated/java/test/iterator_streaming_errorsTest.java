package org.example.patterns;
public class StreamingIteratorTest {
    public static void main(String[] args) {
        StreamingCollection col = new StreamingCollection();
        col.add("a"); col.add("b");
        if (!col.join().equals("streaming:a:b")) throw new AssertionError(col.join());
        System.out.println("ok");
    }
}
