package org.example.patterns;
public class EditorOcpTest {
    public static void main(String[] args) {
        if (new EditorPriceEngine(new EditorTenPercent()).quote(100) != 90) throw new AssertionError();
        System.out.println("ok");
    }
}
