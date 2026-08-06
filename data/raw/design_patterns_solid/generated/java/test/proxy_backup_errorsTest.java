package org.example.patterns;
public class BackupProxyTest {
    public static void main(String[] args) {
        if (!new BackupProxy(true).load("1").equals("real-backup:1")) throw new AssertionError();
        if (!new BackupProxy(false).load("1").equals("denied")) throw new AssertionError();
        System.out.println("ok");
    }
}
