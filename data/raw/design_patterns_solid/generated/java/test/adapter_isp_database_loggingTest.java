package org.example.patterns;
public class DatabaseAdapterTest {
    public static void main(String[] args) {
        DatabaseTarget t = new DatabaseAdapter(new DatabaseLegacyApi());
        if (!t.fetch().equals("modern-database")) throw new AssertionError(t.fetch());
        System.out.println("ok");
    }
}
