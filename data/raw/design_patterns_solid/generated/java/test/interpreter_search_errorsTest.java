package org.example.patterns;
public class SearchInterpreterTest {
    public static void main(String[] args) {
        SearchInterpreter i = new SearchInterpreter();
        if (i.eval("2+3") != 5) throw new AssertionError();
        System.out.println("ok");
    }
}
