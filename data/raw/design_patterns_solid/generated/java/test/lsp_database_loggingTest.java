package org.example.patterns;
public class DatabaseLspTest {
    public static void main(String[] args) {
        DatabaseShape[] arr = new DatabaseShape[] { new DatabaseRectangle(2,3), new DatabaseSquare(4) };
        if (DatabaseLspUtil.total(arr) != 22) throw new AssertionError();
        System.out.println("ok");
    }
}
