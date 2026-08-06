package org.example.patterns;
public class SearchStrategyTest {
    public static void main(String[] args) {
        SearchContext ctx = new SearchContext(new SearchDiscountStrategy());
        if (ctx.execute(10) != 5) throw new AssertionError();
        System.out.println("ok");
    }
}
