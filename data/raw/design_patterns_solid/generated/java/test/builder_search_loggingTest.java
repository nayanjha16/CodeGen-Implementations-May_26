package org.example.patterns;
public class SearchBuilderTest {
    public static void main(String[] args) {
        SearchConfig cfg = new SearchConfig.Builder().name("search-x").limit(3).enabled(false).build();
        if (!cfg.summary().equals("search-x:3:false")) throw new AssertionError(cfg.summary());
        System.out.println("ok");
    }
}
