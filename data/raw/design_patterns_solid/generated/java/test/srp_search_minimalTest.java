package org.example.patterns;
public class SearchSrpTest {
    public static void main(String[] args) {
        SearchRecord r = new SearchRecord("a", 3);
        if (!new SearchFormatter().format(r).equals("a=3")) throw new AssertionError();
        System.out.println("ok");
    }
}
