package org.example.patterns;
public class SearchStateTest {
    public static void main(String[] args) {
        SearchContext ctx = new SearchContext();
        if (!ctx.request().equals("was-off-search")) throw new AssertionError();
        if (!ctx.request().equals("was-on-search")) throw new AssertionError();
        System.out.println("ok");
    }
}
