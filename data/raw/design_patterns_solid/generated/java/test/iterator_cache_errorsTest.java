package org.example.patterns;
public class CacheIteratorTest {
    public static void main(String[] args) {
        CacheCollection col = new CacheCollection();
        col.add("a"); col.add("b");
        if (!col.join().equals("cache:a:b")) throw new AssertionError(col.join());
        System.out.println("ok");
    }
}
