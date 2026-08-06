package org.example.patterns;
public class SearchAdapterTest {
    public static void main(String[] args) {
        SearchTarget t = new SearchAdapter(new SearchLegacyApi());
        if (!t.fetch().equals("modern-search")) throw new AssertionError(t.fetch());
        System.out.println("ok");
    }
}
