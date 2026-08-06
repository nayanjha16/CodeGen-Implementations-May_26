package org.example.patterns;
public class HttpIteratorTest {
    public static void main(String[] args) {
        HttpCollection col = new HttpCollection();
        col.add("a"); col.add("b");
        if (!col.join().equals("http:a:b")) throw new AssertionError(col.join());
        System.out.println("ok");
    }
}
