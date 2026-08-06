package org.example.patterns;
public class SearchIteratorTest {
    public static void main(String[] args) {
        SearchCollection col = new SearchCollection();
        col.add("a"); col.add("b");
        if (!col.join().equals("search:a:b")) throw new AssertionError(col.join());
        System.out.println("ok");
    }
}
