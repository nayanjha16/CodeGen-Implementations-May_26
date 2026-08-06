package org.example.patterns;
public class SearchSingletonTest {
    public static void main(String[] args) {
        SearchSingleton a = SearchSingleton.getInstance();
        SearchSingleton b = SearchSingleton.getInstance();
        a.setValue("search-one");
        if (a != b) throw new AssertionError("not singleton");
        if (!b.getValue().equals("search-one")) throw new AssertionError("state not shared");
        System.out.println("ok");
    }
}
