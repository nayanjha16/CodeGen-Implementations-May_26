package org.example.patterns;
public class SmsSrpTest {
    public static void main(String[] args) {
        SmsRecord r = new SmsRecord("a", 3);
        if (!new SmsFormatter().format(r).equals("a=3")) throw new AssertionError();
        System.out.println("ok");
    }
}
