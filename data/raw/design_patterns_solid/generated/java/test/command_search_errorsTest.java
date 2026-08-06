package org.example.patterns;
public class SearchCommandTest {
    public static void main(String[] args) {
        SearchCommand cmd = new SearchActionCommand(new SearchReceiver(), "x");
        if (!cmd.execute().equals("done-search:x")) throw new AssertionError();
        System.out.println("ok");
    }
}
