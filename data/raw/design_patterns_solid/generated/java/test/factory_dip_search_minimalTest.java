package org.example.patterns;
public class SearchFactoryTest {
    public static void main(String[] args) {
        SearchFactory f = new SearchFactory();
        if (!f.create("basic").operate().equals("basic-search")) throw new AssertionError();
        if (!f.create("premium").operate().equals("premium-search")) throw new AssertionError();
        System.out.println("ok");
    }
}
