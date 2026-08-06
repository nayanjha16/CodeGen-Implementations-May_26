package org.example.patterns;
public class DatabaseFactoryTest {
    public static void main(String[] args) {
        DatabaseFactory f = new DatabaseFactory();
        if (!f.create("basic").operate().equals("basic-database")) throw new AssertionError();
        if (!f.create("premium").operate().equals("premium-database")) throw new AssertionError();
        System.out.println("ok");
    }
}
