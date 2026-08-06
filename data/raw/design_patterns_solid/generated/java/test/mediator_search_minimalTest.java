package org.example.patterns;
public class SearchMediatorTest {
    public static void main(String[] args) {
        SearchMediator m = new SearchMediator();
        new SearchColleague("a", m).send("hi");
        if (!m.history().equals("a->hi")) throw new AssertionError();
        System.out.println("ok");
    }
}
