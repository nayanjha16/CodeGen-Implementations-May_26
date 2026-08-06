package org.example.patterns;
public class SearchDecoratorTest {
    public static void main(String[] args) {
        SearchComponent c = new SearchUpperDecorator(new SearchCore());
        String out = c.process("ab");
        if (!out.equals("SEARCH:AB")) throw new AssertionError(out);
        System.out.println("ok");
    }
}
