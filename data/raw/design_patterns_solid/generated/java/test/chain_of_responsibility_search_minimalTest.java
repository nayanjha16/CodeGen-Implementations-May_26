package org.example.patterns;
public class SearchChainTest {
    public static void main(String[] args) {
        SearchHandler h = new SearchLowHandler();
        h.link(new SearchHighHandler());
        if (!h.handle(2, "m").equals("high-search:m")) throw new AssertionError();
        System.out.println("ok");
    }
}
