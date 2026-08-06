package org.example.patterns;
public class DatabaseChainTest {
    public static void main(String[] args) {
        DatabaseHandler h = new DatabaseLowHandler();
        h.link(new DatabaseHighHandler());
        if (!h.handle(2, "m").equals("high-database:m")) throw new AssertionError();
        System.out.println("ok");
    }
}
