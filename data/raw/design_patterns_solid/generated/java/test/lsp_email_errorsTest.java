package org.example.patterns;
public class EmailLspTest {
    public static void main(String[] args) {
        EmailShape[] arr = new EmailShape[] { new EmailRectangle(2,3), new EmailSquare(4) };
        if (EmailLspUtil.total(arr) != 22) throw new AssertionError();
        System.out.println("ok");
    }
}
