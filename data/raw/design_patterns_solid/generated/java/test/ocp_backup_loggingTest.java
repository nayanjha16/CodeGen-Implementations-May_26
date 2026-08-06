package org.example.patterns;
public class BackupOcpTest {
    public static void main(String[] args) {
        if (new BackupPriceEngine(new BackupTenPercent()).quote(100) != 90) throw new AssertionError();
        System.out.println("ok");
    }
}
