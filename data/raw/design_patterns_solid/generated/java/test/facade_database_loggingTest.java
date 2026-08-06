package org.example.patterns;
public class DatabaseFacadeTest {
    public static void main(String[] args) {
        DatabaseFacade f = new DatabaseFacade();
        if (!f.submit("x").equals("wrote-database:x")) throw new AssertionError();
        System.out.println("ok");
    }
}
