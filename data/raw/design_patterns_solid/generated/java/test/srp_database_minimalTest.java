package org.example.patterns;
public class DatabaseSrpTest {
    public static void main(String[] args) {
        DatabaseRecord r = new DatabaseRecord("a", 3);
        if (!new DatabaseFormatter().format(r).equals("a=3")) throw new AssertionError();
        System.out.println("ok");
    }
}
