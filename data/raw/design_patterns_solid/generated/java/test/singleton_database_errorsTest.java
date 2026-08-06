package org.example.patterns;
public class DatabaseSingletonTest {
    public static void main(String[] args) {
        DatabaseSingleton a = DatabaseSingleton.getInstance();
        DatabaseSingleton b = DatabaseSingleton.getInstance();
        a.setValue("database-one");
        if (a != b) throw new AssertionError("not singleton");
        if (!b.getValue().equals("database-one")) throw new AssertionError("state not shared");
        System.out.println("ok");
    }
}
