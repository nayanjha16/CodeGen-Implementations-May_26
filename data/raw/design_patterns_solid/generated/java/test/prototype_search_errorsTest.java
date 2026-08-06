package org.example.patterns;
public class SearchPrototypeTest {
    public static void main(String[] args) {
        SearchPrototype a = new SearchPrototype("search", 2);
        SearchPrototype b = a.copy();
        b.setLabel("search-copy");
        if (a.describe().equals(b.describe())) throw new AssertionError();
        System.out.println("ok");
    }
}
