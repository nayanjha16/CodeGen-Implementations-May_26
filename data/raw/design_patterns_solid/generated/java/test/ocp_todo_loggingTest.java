package org.example.patterns;
public class TodoOcpTest {
    public static void main(String[] args) {
        if (new TodoPriceEngine(new TodoTenPercent()).quote(100) != 90) throw new AssertionError();
        System.out.println("ok");
    }
}
